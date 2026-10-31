"""Week-1 integration slice: create -> stored -> notified -> logged."""

import pytest

# These modules belong to other milestones (M1/M2). Until they are merged,
# skip this integration test instead of erroring out at collection time.
# Only *missing* modules are skipped; real import bugs still fail the run.
_database = pytest.importorskip(
    "helpdesk.database.database", exc_type=ModuleNotFoundError
)
_activity = pytest.importorskip(
    "helpdesk.repositories.activity_repository", exc_type=ModuleNotFoundError
)
_staff = pytest.importorskip(
    "helpdesk.repositories.staff_repository", exc_type=ModuleNotFoundError
)
_tickets = pytest.importorskip(
    "helpdesk.repositories.ticket_repository", exc_type=ModuleNotFoundError
)
_service = pytest.importorskip(
    "helpdesk.services.ticket_service", exc_type=ModuleNotFoundError
)

from helpdesk.patterns.observer.observer import ActivityLogObserver  # noqa: E402
from helpdesk.patterns.observer.publisher import TicketEventPublisher  # noqa: E402


class RecordingObserver:
    def __init__(self):
        self.received = []

    def update(self, event):
        self.received.append(event)


@pytest.fixture
def database(tmp_path):
    db = _database.Database(tmp_path / "helpdesk_test.db")
    db.initialize()
    return db


@pytest.fixture
def activity_repository(database):
    return _activity.ActivityRepository(database)


@pytest.fixture
def recording_observer():
    return RecordingObserver()


@pytest.fixture
def service(database, activity_repository, recording_observer):
    publisher = TicketEventPublisher()
    publisher.subscribe(ActivityLogObserver(activity_repository))
    publisher.subscribe(recording_observer)
    return _service.TicketService(
        _tickets.TicketRepository(database),
        _staff.StaffRepository(database),
        publisher,
    )


def test_create_ticket_persists_and_notifies(
    service,
    activity_repository,
    recording_observer,
):
    ticket = service.create_ticket(
        title="VPN drops every hour",
        description="Connection resets at :55 every hour",
        category="TECHNICAL",
        priority="HIGH",
    )

    assert ticket.id is not None
    assert service.list_tickets(status="OPEN")

    records = activity_repository.list_for(ticket.id)
    assert [record.action for record in records] == ["TicketCreated"]
    assert recording_observer.received, "publisher did not notify test observer"
    assert recording_observer.received[0].ticket_id == ticket.id

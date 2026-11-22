"""Shared fixtures: one isolated temp database per test (NFR-4)."""

import pytest

from helpdesk.database.database import Database
from helpdesk.patterns.observer.publisher import TicketEventPublisher
from helpdesk.repositories.activity_repository import ActivityRepository
from helpdesk.repositories.staff_repository import StaffRepository
from helpdesk.repositories.ticket_repository import TicketRepository
from helpdesk.services.assignment_service import AssignmentService
from helpdesk.services.ticket_service import TicketService


@pytest.fixture
def database(tmp_path):
    db = Database(tmp_path / "test_helpdesk.db")
    db.initialize()
    return db


@pytest.fixture
def ticket_repository(database):
    return TicketRepository(database)


@pytest.fixture
def staff_repository(database):
    return StaffRepository(database)


@pytest.fixture
def activity_repository(database):
    return ActivityRepository(database)


class RecordingObserver:
    """Observer: test double for asserting published events."""

    def __init__(self):
        self.received = []

    def update(self, event):
        self.received.append(event)

    @property
    def names(self):
        return [event.name for event in self.received]


@pytest.fixture
def recording_observer():
    return RecordingObserver()


@pytest.fixture
def publisher(recording_observer):
    bus = TicketEventPublisher()
    bus.subscribe(recording_observer)
    return bus


@pytest.fixture
def service(database, publisher):
    return TicketService(
        TicketRepository(database),
        StaffRepository(database),
        publisher,
    )


@pytest.fixture
def assignment(database, publisher):
    return AssignmentService(
        database,
        publisher=publisher,
        ticket_repository=TicketRepository(database),
        staff_repository=StaffRepository(database),
    )

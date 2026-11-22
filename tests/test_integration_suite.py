"""Week-3 M3 cross-milestone acceptance suite.

Every test here crosses at least two pattern boundaries; the single-pattern
behavior lives in test_state / test_strategy / test_factory / test_decorator.
"""

from dataclasses import replace
from datetime import UTC, datetime

import pytest

from helpdesk.database.database import Database
from helpdesk.database.seed import seed
from helpdesk.models.exceptions import (
    DomainError,
    InvalidTransitionError,
    ValidationError,
)
from helpdesk.patterns.decorator.notification_decorators import (
    LoggingNotificationDecorator,
    UrgentNotificationDecorator,
)
from helpdesk.patterns.observer.events import TicketCreated
from helpdesk.patterns.observer.observers import ConsoleNotificationObserver
from helpdesk.patterns.observer.publisher import TicketEventPublisher
from helpdesk.repositories.staff_repository import StaffRepository
from helpdesk.repositories.ticket_repository import TicketRepository
from helpdesk.services.assignment_service import AssignmentService
from helpdesk.services.ticket_service import TicketService


@pytest.fixture
def seeded_services(tmp_path):
    db = Database(tmp_path / "acceptance.db")
    db.initialize()
    seed(db)
    publisher = TicketEventPublisher()
    tickets = TicketRepository(db)
    staff = StaffRepository(db)
    return TicketService(tickets, staff, publisher), AssignmentService(
        db, publisher=publisher, ticket_repository=tickets, staff_repository=staff
    ), publisher


def test_seeded_auto_assignment_uses_the_two_free_staff(seeded_services):
    service, assignment, _ = seeded_services
    for title in ("First new ticket", "Second new ticket"):
        ticket = service.create_ticket(
            title=title, description="A freshly created demo ticket.",
            category="TECHNICAL", component="email",
        )
        assignment.assign(ticket.id)
    assigned = [t.assigned_staff_id for t in service.list_tickets()
                if t.title in ("First new ticket", "Second new ticket")]
    assert assigned == [5, 6]


def test_seeded_reopen_window_is_demo_ready(seeded_services):
    service, _, _ = seeded_services
    recent = next(t for t in service.list_tickets() if t.title == "Outage came back")
    old = next(t for t in service.list_tickets() if t.title == "Dead dock station")
    assert service.transition(recent.id, "REOPEN").status_code == "IN_PROGRESS"
    with pytest.raises(InvalidTransitionError, match="7 days"):
        service.transition(old.id, "REOPEN")


def test_service_rejects_unknown_category_without_touching_storage(service):
    with pytest.raises(Exception, match="Category"):
        service.create_ticket(
            title="Unknown kind", description="A ticket with a retired category.",
            category="SOFTWARE",
        )
    assert service.list_tickets() == []


def test_service_requires_category_specific_fields(service):
    with pytest.raises(ValidationError, match="affected_account"):
        service.create_ticket(
            title="Account issue", description="An account without the required field.",
            category="ACCOUNT",
        )
    assert service.list_tickets() == []


def test_resolve_without_note_does_not_change_state(service):
    ticket = service.create_ticket(
        title="No note ticket", description="Resolution attempts without a note.",
        category="TECHNICAL", component="email",
    )
    with pytest.raises(ValidationError, match="resolution note"):
        service.transition(ticket.id, "RESOLVED", note="")
    assert service.get_ticket(ticket.id).status_code == "OPEN"


def test_observer_failure_does_not_break_the_use_case(database):
    class BrokenObserver:
        def update(self, event):
            raise RuntimeError("observer exploded")

    publisher = TicketEventPublisher()
    publisher.subscribe(BrokenObserver())
    service = TicketService(
        TicketRepository(database), StaffRepository(database), publisher
    )
    ticket = service.create_ticket(
        title="Still works", description="A broken observer must not stop creation.",
        category="TECHNICAL", component="email",
    )
    assert ticket.id is not None


def test_unsubscribing_an_observer_stops_notifications(service, recording_observer, publisher):
    publisher.unsubscribe(recording_observer)
    service.create_ticket(
        title="Silent ticket", description="No observers should see this ticket.",
        category="TECHNICAL", component="email",
    )
    assert recording_observer.received == []


def test_event_messages_are_immutable_across_decorators():
    event = TicketCreated(
        ticket_id=7, occurred_at=datetime.now(UTC),
        title="Critical", category="TECHNICAL", priority="CRITICAL",
    )
    urgent = replace(event, message=f"[URGENT] {event.message}")
    assert event.message.startswith("Ticket 'Critical'")
    assert urgent.message.startswith("[URGENT] Ticket 'Critical'")
    assert urgent is not event


def test_decorator_chain_can_be_built_in_different_orders(capsys):
    for stack in (
        lambda: LoggingNotificationDecorator(UrgentNotificationDecorator(
            ConsoleNotificationObserver())),
        lambda: UrgentNotificationDecorator(LoggingNotificationDecorator(
            ConsoleNotificationObserver())),
    ):
        event = TicketCreated(
            ticket_id=8, occurred_at=datetime.now(UTC),
            title="Boom", category="TECHNICAL", priority="CRITICAL",
        )
        stack().update(event)
    output = capsys.readouterr().out
    assert output.count("[LOG]") == 2
    # When Logging is the inner decorator the [URGENT] prefix appears inside
    # the [LOG] line too, so count console deliveries rather than raw tokens.
    assert sum("[console]" in line for line in output.splitlines()) == 2


def test_assignment_events_reach_observers(service, assignment, staff_repository,
                                           recording_observer):
    staff_repository.add("Maya Chen")
    ticket = service.create_ticket(
        title="Eventful assignment", description="Assignment must publish an event.",
        category="TECHNICAL", component="email",
    )
    recording_observer.received.clear()
    assignment.assign(ticket.id, 1)
    assert recording_observer.names == ["StaffAssignedEvent"]
    assert "staff #1" in recording_observer.received[0].message.lower()


def test_status_changes_survive_a_repository_round_trip(service):
    ticket = service.create_ticket(
        title="Persist the state", description="State changes must survive a reload.",
        category="TECHNICAL", component="email",
    )
    service.transition(ticket.id, "IN_PROGRESS")
    service.transition(ticket.id, "RESOLVED", note="The fix is complete")
    reloaded = service.get_ticket(ticket.id)
    assert reloaded.status_code == "RESOLVED"
    assert reloaded.resolution_note == "The fix is complete"
    assert reloaded.closed_at is None

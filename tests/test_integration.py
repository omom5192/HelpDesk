"""End-to-end integration: Observer + Decorator + Factory + State + Strategy."""

from datetime import UTC, datetime

from helpdesk.database.database import Database
from helpdesk.models.exceptions import DomainError
from helpdesk.patterns.decorator.notification_decorators import (
    LoggingNotificationDecorator,
    UrgentNotificationDecorator,
)
from helpdesk.patterns.observer.observers import (
    ActivityLogObserver,
    ConsoleNotificationObserver,
)
from helpdesk.patterns.observer.publisher import TicketEventPublisher
from helpdesk.patterns.strategy.ordering_strategies import DeadlineOrderingStrategy
from helpdesk.repositories.activity_repository import ActivityRepository
from helpdesk.repositories.staff_repository import StaffRepository
from helpdesk.repositories.ticket_repository import TicketRepository
from helpdesk.services.ticket_service import TicketService


def build_stacked_service(database):
    publisher = TicketEventPublisher()
    publisher.subscribe(
        LoggingNotificationDecorator(
            UrgentNotificationDecorator(ConsoleNotificationObserver())
        )
    )
    publisher.subscribe(ActivityLogObserver(ActivityRepository(database)))
    return TicketService(
        TicketRepository(database), StaffRepository(database), publisher
    ), publisher


def test_create_ticket_notifies_and_logs_the_activity(database, tmp_path):
    service, _ = build_stacked_service(database)
    ticket = service.create_ticket(
        title="Email outage again",
        description="The outbound mail queue stopped draining again.",
        category="TECHNICAL",
        priority="CRITICAL",
        component="email",
    )
    records = ActivityRepository(database).list_for(ticket.id)
    assert [record.action for record in records] == ["TicketCreated"]
    assert "outage" in records[0].description.lower()


def test_decorator_stack_logs_and_prefixes_urgent_notifications(capsys, database):
    service, _ = build_stacked_service(database)
    service.create_ticket(
        title="Critical outage",
        description="The entire campus network is down right now.",
        category="TECHNICAL",
        priority="CRITICAL",
        component="network",
    )
    output = capsys.readouterr().out
    assert "[LOG]" in output
    assert "[URGENT]" in output
    assert "[console]" in output


def test_full_lifecycle_publishes_every_status_change(service, recording_observer):
    ticket = service.create_ticket(
        title="Full lifecycle",
        description="This ticket walks through the entire lifecycle.",
        category="TECHNICAL",
        component="email",
    )
    service.transition(ticket.id, "IN_PROGRESS")
    service.transition(ticket.id, "RESOLVED", note="Patched the mail server")
    service.transition(ticket.id, "CLOSED")
    service.transition(ticket.id, "REOPEN")

    assert service.get_ticket(ticket.id).status_code == "IN_PROGRESS"
    assert recording_observer.names == [
        "TicketCreated",
        "TicketStatusChanged",
        "TicketStatusChanged",
        "TicketStatusChanged",
        "TicketStatusChanged",
    ]


def test_all_three_categories_create_through_the_registry(service):
    technical = service.create_ticket(
        title="DNS is slow", description="DNS answers are slow during peak hours.",
        category="TECHNICAL", component="network",
    )
    account = service.create_ticket(
        title="Account locked", description="The registrar account is locked out.",
        category="ACCOUNT", affected_account="registrar.office",
    )
    hardware = service.create_ticket(
        title="PC will not boot", description="The lab PC does not power on.",
        category="HARDWARE", asset_tag="PC-1234", location="Lab 2",
    )
    assert technical.technical_component == "network"
    assert account.affected_account == "registrar.office"
    assert hardware.asset_tag == "PC-1234"
    assert service.get_ticket(hardware.id).location == "Lab 2"


def test_assignment_is_refused_for_resolved_tickets(service, assignment, staff_repository):
    member = staff_repository.add("Maya Chen")
    ticket = service.create_ticket(
        title="Assign after close",
        description="This ticket must not be assignable once resolved.",
        category="TECHNICAL", component="email",
    )
    service.transition(ticket.id, "RESOLVED", note="Fixed before assignment")
    try:
        assignment.assign(ticket.id, member.id)
    except DomainError as exc:
        assert "BR-7" in str(exc)
    else:
        raise AssertionError("BR-7 was not enforced")


def test_auto_assignment_prefers_the_least_loaded_staff(service, assignment, staff_repository):
    people = [staff_repository.add(f"Staff {index}") for index in range(3)]
    # Load staff 0 and 1 with one OPEN ticket each; staff 2 stays free.
    for index in (0, 1):
        ticket = service.create_ticket(
            title=f"Initial load {index}",
            description=f"Ticket that loads staff member {index}.",
            category="TECHNICAL", component="email",
        )
        assignment.assign(ticket.id, people[index].id)

    fresh = service.create_ticket(
        title="Needs an owner",
        description="A new ticket that should go to the least loaded member.",
        category="TECHNICAL", component="email",
    )
    chosen = assignment.assign(fresh.id)
    assert chosen.assigned_staff_id == people[2].id
    assert assignment.candidate_overview()[-1][2] == 1


def test_ordering_strategy_switch_changes_service_output(service):
    service.create_ticket(
        title="No deadline", description="A ticket without any deadline value.",
        category="TECHNICAL", component="email", priority="LOW",
    )
    service.create_ticket(
        title="With deadline", description="A ticket that has an early deadline.",
        category="TECHNICAL", component="email", priority="HIGH",
        deadline=datetime(2026, 11, 3, 9, 0, tzinfo=UTC),
    )
    service.set_ordering_strategy(DeadlineOrderingStrategy())
    assert service.list_tickets()[0].title == "With deadline"


def test_composition_root_builds_a_usable_menu_object(tmp_path):
    from helpdesk.main import build_application

    menu = build_application(str(tmp_path / "app.db"))
    assert hasattr(menu, "run")
    assert hasattr(menu, "_service")
    assert hasattr(menu, "_assignment")

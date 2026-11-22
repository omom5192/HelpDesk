"""Week-3 M1: persistence edge cases and schema hardening."""

from datetime import UTC, datetime, timedelta

import pytest

from helpdesk.models.exceptions import NotFoundError
from helpdesk.models.ticket import HardwareTicket, TechnicalTicket, Ticket
from helpdesk.repositories.staff_repository import StaffRepository

WHEN = datetime(2026, 11, 2, 9, 0, tzinfo=UTC)


def technical_ticket(**overrides):
    payload = dict(
        title="Router is down",
        description="The main router stopped responding this morning.",
        category="TECHNICAL",
        priority="HIGH",
        created_at=WHEN,
        updated_at=WHEN,
        deadline=WHEN + timedelta(days=2),
        technical_component="network",
    )
    payload.update(overrides)
    return TechnicalTicket(**payload)


def test_save_assigns_an_id_and_round_trips_every_field(ticket_repository):
    ticket = ticket_repository.save(technical_ticket())
    assert ticket.id is not None

    loaded = ticket_repository.get(ticket.id)
    assert loaded == ticket
    assert loaded.deadline == WHEN + timedelta(days=2)
    assert loaded.technical_component == "network"
    assert loaded.status_code == "OPEN"


def test_save_updates_an_existing_ticket(ticket_repository):
    ticket = ticket_repository.save(technical_ticket())
    ticket.priority = "CRITICAL"
    ticket.start_progress()
    ticket_repository.save(ticket)

    loaded = ticket_repository.get(ticket.id)
    assert loaded.priority == "CRITICAL"
    assert loaded.status_code == "IN_PROGRESS"


def test_get_missing_ticket_raises_not_found(ticket_repository):
    with pytest.raises(NotFoundError, match="#999"):
        ticket_repository.get(999)


def test_find_combines_several_filters(ticket_repository):
    ticket_repository.save(technical_ticket(priority="HIGH"))
    ticket_repository.save(
        Ticket(
            title="Low priority issue",
            description="A different, low priority technical issue.",
            category="TECHNICAL",
            priority="LOW",
            technical_component="email",
            created_at=WHEN,
        )
    )
    assert len(ticket_repository.find(priority="HIGH", status="OPEN")) == 1
    assert ticket_repository.find(priority="CRITICAL") == []
    assert len(ticket_repository.find(category="TECHNICAL")) == 2


def test_find_maps_staff_id_to_assigned_staff_id(ticket_repository, staff_repository):
    member = staff_repository.add("Maya Chen")
    ticket_repository.save(technical_ticket(assigned_staff_id=member.id))
    assert len(ticket_repository.find(staff_id=member.id)) == 1


def test_status_is_stored_as_an_uppercase_code(ticket_repository, database):
    ticket = ticket_repository.save(technical_ticket())
    with database.connection() as conn:
        row = conn.execute("SELECT status FROM tickets WHERE id = ?", (ticket.id,)).fetchone()
    assert row["status"] == "OPEN"


def test_product_class_is_restored_from_the_category_column(ticket_repository):
    hardware = ticket_repository.save(
        HardwareTicket(
            title="Laptop will not boot",
            description="The laptop remains black after pressing power.",
            category="HARDWARE",
            priority="LOW",
            created_at=WHEN,
            asset_tag="PC-1234",
            location="Lab 2",
        )
    )
    loaded = ticket_repository.get(hardware.id)
    assert isinstance(loaded, HardwareTicket)
    assert loaded.asset_tag == "PC-1234"


def test_activity_repository_round_trips_datetimes(activity_repository, ticket_repository):
    ticket = ticket_repository.save(technical_ticket())
    activity_repository.append(ticket.id, "TicketCreated", "Created", WHEN)
    records = activity_repository.list_for(ticket.id)
    assert len(records) == 1
    assert records[0].action == "TicketCreated"
    assert records[0].created_at == WHEN
    assert activity_repository.list_for(ticket.id + 1) == []


def test_schema_indexes_exist(database):
    with database.connection() as conn:
        names = {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'index'"
            ).fetchall()
        }
    assert {
        "idx_tickets_status", "idx_tickets_priority", "idx_tickets_category",
        "idx_tickets_staff_id", "idx_tickets_deadline", "idx_activity_ticket",
    } <= names


def test_staff_workloads_count_only_open_and_in_progress(ticket_repository, staff_repository):
    member = staff_repository.add("Maya Chen")
    ticket_repository.save(technical_ticket(assigned_staff_id=member.id))
    running = ticket_repository.save(
        technical_ticket(title="Running ticket", assigned_staff_id=member.id)
    )
    running.start_progress()
    ticket_repository.save(running)
    closed = ticket_repository.save(
        technical_ticket(title="Closed ticket", assigned_staff_id=member.id)
    )
    closed.close()
    ticket_repository.save(closed)

    assert staff_repository.count_open_workloads(member.id) == 2

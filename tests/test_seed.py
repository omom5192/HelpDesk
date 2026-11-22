"""Week-3 M1: deterministic, idempotent demo seed."""

from datetime import UTC, datetime, timedelta

import pytest

from helpdesk.database.database import Database
from helpdesk.database.seed import FAKE_NOW, seed
from helpdesk.models.exceptions import InvalidTransitionError
from helpdesk.models.ticket import AccountTicket, HardwareTicket, TechnicalTicket
from helpdesk.repositories.staff_repository import StaffRepository
from helpdesk.repositories.ticket_repository import TicketRepository


@pytest.fixture
def seeded(tmp_path):
    db = Database(tmp_path / "seeded.db")
    db.initialize()
    counts = seed(db)
    return db, counts


def test_seed_populates_six_staff_and_eleven_tickets(seeded):
    db, counts = seeded
    assert counts == {"staff": 6, "tickets": 11}
    assert len(StaffRepository(db).list_all()) == 6
    assert len(TicketRepository(db).find()) == 11


def test_seed_is_idempotent(seeded):
    db, _ = seeded
    assert seed(db) == {"staff": 0, "tickets": 0}
    assert len(TicketRepository(db).find()) == 11


def test_staff_timestamps_are_deterministic_and_ordered(seeded):
    db, _ = seeded
    staff = StaffRepository(db).list_all()
    assert [member.created_at for member in staff] == [
        FAKE_NOW - timedelta(days=6 - index) for index in range(6)
    ]


def test_ticket_status_distribution(seeded):
    db, _ = seeded
    tickets = TicketRepository(db).find()
    statuses = [ticket.status_code for ticket in tickets]
    assert statuses.count("OPEN") == 7
    assert statuses.count("IN_PROGRESS") == 1
    assert statuses.count("RESOLVED") == 1
    assert statuses.count("CLOSED") == 2


def test_workload_distribution_supports_auto_assignment(seeded):
    db, _ = seeded
    workloads = StaffRepository(db).count_open_workloads()
    assert workloads == {1: 2, 2: 2, 3: 1, 4: 1}


def test_seed_uses_canonical_tokens_and_category_products(seeded):
    db, _ = seeded
    tickets = TicketRepository(db).find()
    assert {ticket.category for ticket in tickets} == {
        "TECHNICAL", "ACCOUNT", "HARDWARE"
    }
    assert {ticket.priority for ticket in tickets} <= {
        "LOW", "MEDIUM", "HIGH", "CRITICAL"
    }
    assert all(isinstance(ticket.technical_component, str) for ticket in tickets
               if isinstance(ticket, TechnicalTicket))
    assert all(isinstance(ticket.affected_account, str) for ticket in tickets
               if isinstance(ticket, AccountTicket))
    assert all(
        isinstance(ticket.asset_tag, str) and isinstance(ticket.location, str)
        for ticket in tickets if isinstance(ticket, HardwareTicket)
    )


def test_seed_contains_both_br2_reopen_examples(seeded):
    db, _ = seeded
    tickets = TicketRepository(db).find()
    recent = next(t for t in tickets if t.title == "Outage came back")
    old = next(t for t in tickets if t.title == "Dead dock station")

    assert datetime.now(UTC) - recent.closed_at < timedelta(days=3)
    assert datetime.now(UTC) - old.closed_at > timedelta(days=9)

    recent.reopen()
    assert recent.status_code == "IN_PROGRESS"
    with pytest.raises(InvalidTransitionError, match="7 days"):
        old.reopen()


def test_seeded_ticket_hydrates_with_a_state_object(seeded):
    db, _ = seeded
    ticket = TicketRepository(db).get(1)
    assert ticket.status_code == "OPEN"
    assert ticket.status_display == "Open"
    assert ticket.created_at is not None

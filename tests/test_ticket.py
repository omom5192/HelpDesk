"""Ticket model tests — dataclass semantics.

We only pin creation defaults and the view shape here; status-transition
behavior arrives later with the State pattern (M2's milestone).
"""

from datetime import UTC, datetime

from helpdesk.models.ticket import Ticket

WHEN = datetime(2026, 11, 5, 9, 0, tzinfo=UTC)


def make_ticket():
    return Ticket(
        title="Login problem",
        description="Cannot log in at all",
        category="ACCOUNT",
        priority="HIGH",
        created_at=WHEN,
        updated_at=WHEN,
    )


def test_ticket_starts_open_with_no_database_identity():
    ticket = make_ticket()
    assert ticket.id is None
    assert ticket.status == "OPEN"
    assert ticket.status_code == "OPEN"


def test_get_details_reports_schema_fields():
    details = make_ticket().get_details()
    assert details["Title"] == "Login problem"
    assert details["Category"] == "ACCOUNT"
    assert details["Priority"] == "HIGH"
    assert details["Status"] == "OPEN"

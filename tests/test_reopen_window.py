"""BR-2: 7-day reopen window (deadline rules are explicit and tested)."""

from datetime import UTC, datetime, timedelta

import pytest

from helpdesk.models.exceptions import InvalidTransitionError
from helpdesk.models.ticket import Ticket
from helpdesk.patterns.state.base_state import REOPEN_WINDOW_DAYS

WHEN = datetime(2026, 11, 2, 9, 0, tzinfo=UTC)


def closed_ticket(closed_at):
    ticket = Ticket(
        title="Closed ticket",
        description="A ticket that has already been closed.",
        category="TECHNICAL",
        technical_component="network",
        created_at=WHEN,
        resolution_note="Fixed the issue",
    )
    ticket.set_state_from_code("CLOSED")
    ticket.closed_at = closed_at
    return ticket


def test_window_constant_is_seven_days():
    assert REOPEN_WINDOW_DAYS == 7


def test_reopen_works_one_day_after_closing():
    ticket = closed_ticket(datetime.now(UTC) - timedelta(days=1))
    ticket.reopen()
    assert ticket.status_code == "IN_PROGRESS"


def test_reopen_is_inclusive_on_day_seven():
    ticket = closed_ticket(datetime.now(UTC) - timedelta(days=7))
    ticket.reopen()  # scheduling jitter at the boundary is tolerated
    assert ticket.status_code == "IN_PROGRESS"


def test_reopen_fails_one_second_past_the_boundary():
    ticket = closed_ticket(datetime.now(UTC) - timedelta(days=7, seconds=1))
    with pytest.raises(InvalidTransitionError, match="7 days"):
        ticket.reopen()
    assert ticket.status_code == "CLOSED"


def test_reopen_fails_long_after_the_window():
    ticket = closed_ticket(datetime.now(UTC) - timedelta(days=30))
    with pytest.raises(InvalidTransitionError, match="window expired"):
        ticket.reopen()


def test_closed_without_a_timestamp_has_a_clear_error():
    ticket = closed_ticket(None)
    with pytest.raises(InvalidTransitionError, match="without a timestamp"):
        ticket.reopen()


def test_a_successful_reopen_clears_closed_at_and_the_old_note():
    ticket = closed_ticket(datetime.now(UTC) - timedelta(days=2))
    ticket.reopen()
    assert ticket.closed_at is None
    assert ticket.resolution_note is None


def test_service_reopen_persists_and_publishes_the_change(service, recording_observer):
    ticket = service.create_ticket(
        title="Reopen me", description="This ticket gets closed and reopened.",
        category="TECHNICAL", component="email",
    )
    service.transition(ticket.id, "CLOSED")
    service.transition(ticket.id, "REOPEN")
    assert service.get_ticket(ticket.id).status_code == "IN_PROGRESS"
    assert "TicketStatusChanged" in recording_observer.names

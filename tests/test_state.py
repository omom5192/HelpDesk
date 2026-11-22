"""State pattern: Context + ConcreteStates (BR-1 lifecycle)."""

from datetime import UTC, datetime, timedelta

import pytest

from helpdesk.models.exceptions import InvalidTransitionError, ValidationError
from helpdesk.models.ticket import Ticket
from helpdesk.patterns.state.states import (
    CLOSED_STATE,
    IN_PROGRESS_STATE,
    OPEN_STATE,
    RESOLVED_STATE,
    OpenState,
    state_for,
)

WHEN = datetime(2026, 11, 5, 9, 0, tzinfo=UTC)


def make_ticket(**overrides):
    payload = dict(
        title="Login problem",
        description="Cannot log in at all",
        category="ACCOUNT",
        priority="HIGH",
        created_at=WHEN,
        updated_at=WHEN,
    )
    payload.update(overrides)
    return Ticket(**payload)


def test_new_ticket_starts_in_open_state():
    ticket = make_ticket()
    assert ticket.state is OPEN_STATE
    assert ticket.status_code == "OPEN"
    assert ticket.status_display == "Open"


def test_status_is_an_alias_of_status_code():
    ticket = make_ticket()
    assert ticket.status == ticket.status_code


def test_start_progress_from_open():
    ticket = make_ticket()
    ticket.start_progress()
    assert ticket.state is IN_PROGRESS_STATE
    assert ticket.status_code == "IN_PROGRESS"


def test_start_progress_twice_is_rejected_with_a_reason():
    ticket = make_ticket()
    ticket.start_progress()
    with pytest.raises(InvalidTransitionError, match="already in progress"):
        ticket.start_progress()
    assert ticket.status_code == "IN_PROGRESS"


def test_resolve_from_open_requires_and_stores_a_note():
    ticket = make_ticket()
    ticket.resolve("Reset the password")
    assert ticket.state is RESOLVED_STATE
    assert ticket.resolution_note == "Reset the password"


def test_resolve_without_a_real_note_is_rejected():
    with pytest.raises(ValidationError, match="resolution note"):
        make_ticket().resolve("   ")


def test_resolve_twice_is_rejected():
    ticket = make_ticket()
    ticket.resolve("Reset the password")
    with pytest.raises(InvalidTransitionError, match="already resolved"):
        ticket.resolve("Reset it again")


def test_resolved_ticket_can_be_closed_and_gets_a_timestamp():
    ticket = make_ticket()
    ticket.resolve("Reset the password")
    ticket.close()
    assert ticket.state is CLOSED_STATE
    assert ticket.closed_at is not None


def test_in_progress_cannot_be_closed_before_resolution():
    ticket = make_ticket()
    ticket.start_progress()
    with pytest.raises(InvalidTransitionError, match="must be resolved first"):
        ticket.close()
    assert ticket.status_code == "IN_PROGRESS"


def test_in_progress_cannot_be_reopened():
    ticket = make_ticket()
    ticket.start_progress()
    with pytest.raises(InvalidTransitionError, match="not resolved/closed"):
        ticket.reopen()


def test_resolved_cannot_start_progress_without_reopening():
    ticket = make_ticket()
    ticket.resolve("Reset the password")
    with pytest.raises(InvalidTransitionError, match="reopen it first"):
        ticket.start_progress()


def test_open_ticket_cannot_be_reopened():
    with pytest.raises(InvalidTransitionError, match="already open"):
        make_ticket().reopen()


def test_closed_ticket_rejects_all_forward_transitions():
    ticket = make_ticket()
    ticket.close()
    with pytest.raises(InvalidTransitionError):
        ticket.start_progress()
    with pytest.raises(InvalidTransitionError):
        ticket.resolve("Already done")
    with pytest.raises(InvalidTransitionError):
        ticket.close()


def test_open_can_be_closed_directly_as_a_duplicate():
    ticket = make_ticket()
    ticket.close()
    assert ticket.status_code == "CLOSED"
    assert ticket.closed_at is not None


def test_reopen_clears_the_old_resolution():
    ticket = make_ticket()
    ticket.resolve("Reset the password")
    ticket.reopen()
    assert ticket.status_code == "IN_PROGRESS"
    assert ticket.resolution_note is None
    assert ticket.closed_at is None


def test_transition_updates_the_updated_at_timestamp():
    ticket = make_ticket(updated_at=WHEN)
    ticket.start_progress()
    assert ticket.updated_at is not None
    assert ticket.updated_at > WHEN


def test_state_for_maps_all_codes_and_known_states_are_singletons():
    assert state_for("OPEN") is OPEN_STATE
    assert state_for("IN_PROGRESS") is IN_PROGRESS_STATE
    assert state_for("RESOLVED") is RESOLVED_STATE
    assert state_for("CLOSED") is CLOSED_STATE
    assert isinstance(OPEN_STATE, OpenState)
    assert OpenState() is not OPEN_STATE  # shared default, not an enforced singleton


def test_state_for_rejects_an_unknown_code():
    with pytest.raises(ValueError, match="Unknown ticket status"):
        state_for("PURPLE")


def test_context_transition_helper_maps_action_tokens():
    ticket = make_ticket()
    ticket.transition("IN_PROGRESS")
    assert ticket.status_code == "IN_PROGRESS"
    ticket.transition("RESOLVE", note="Fixed by hand")
    assert ticket.status_code == "RESOLVED"
    ticket.transition("CLOSE")
    assert ticket.status_code == "CLOSED"
    with pytest.raises(InvalidTransitionError, match="Unknown"):
        ticket.transition("TELEPORT")


def test_reopen_after_the_window_is_refused():
    ticket = make_ticket()
    ticket.close()
    ticket.closed_at = datetime.now(UTC) - timedelta(days=8)
    with pytest.raises(InvalidTransitionError, match="7 days"):
        ticket.reopen()

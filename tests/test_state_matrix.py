"""Week-3 audit: the full BR-1 state x action matrix.

Keeping this table as executable documentation makes silent no-ops and
accidental transitions impossible to merge unnoticed.
"""

from datetime import UTC, datetime

import pytest

from helpdesk.models.exceptions import InvalidTransitionError, ValidationError
from helpdesk.models.ticket import Ticket

NOTE = "A valid resolution note"

# Rows = current state; columns = requested action.
ALLOWED = {
    "OPEN": {"START": True, "RESOLVE": True, "CLOSE": True, "REOPEN": False},
    "IN_PROGRESS": {"START": False, "RESOLVE": True, "CLOSE": False, "REOPEN": False},
    "RESOLVED": {"START": False, "RESOLVE": False, "CLOSE": True, "REOPEN": True},
    "CLOSED": {"START": False, "RESOLVE": False, "CLOSE": False, "REOPEN": True},
}


def ticket_in(status: str) -> Ticket:
    ticket = Ticket(
        title="Matrix ticket",
        description="Used for the exhaustive transition matrix.",
        category="TECHNICAL",
        technical_component="email",
        created_at=datetime(2026, 11, 1, 9, 0, tzinfo=UTC),
    )
    ticket.set_state_from_code(status)
    if status == "CLOSED":
        ticket.closed_at = datetime.now(UTC)  # inside the BR-2 window
    return ticket


def request(ticket: Ticket, action: str) -> None:
    if action == "START":
        ticket.start_progress()
    elif action == "RESOLVE":
        ticket.resolve(NOTE)
    elif action == "CLOSE":
        ticket.close()
    elif action == "REOPEN":
        ticket.reopen()
    else:
        raise AssertionError(f"Unknown matrix action {action}")


@pytest.mark.parametrize("status", list(ALLOWED))
@pytest.mark.parametrize("action", ["START", "RESOLVE", "CLOSE", "REOPEN"])
def test_every_cell_of_the_matrix(status, action):
    ticket = ticket_in(status)
    if ALLOWED[status][action]:
        request(ticket, action)
        assert ticket.status_code != "PURPLE"  # a real state object still exists
        expected = {
            "START": "IN_PROGRESS",
            "RESOLVE": "RESOLVED",
            "CLOSE": "CLOSED",
            "REOPEN": "IN_PROGRESS",
        }[action]
        assert ticket.status_code == expected
    else:
        with pytest.raises(InvalidTransitionError, match="Cannot"):
            request(ticket, action)
        assert ticket.status_code == status  # rejected transition is a no-op


@pytest.mark.parametrize("status", list(ALLOWED))
@pytest.mark.parametrize("action", ["START", "RESOLVE", "CLOSE", "REOPEN"])
def test_rejections_always_carry_an_explanatory_message(status, action):
    if ALLOWED[status][action]:
        pytest.skip("cell is allowed")
    ticket = ticket_in(status)
    with pytest.raises(InvalidTransitionError) as caught:
        request(ticket, action)
    assert str(caught.value).strip()


def test_matrix_is_exhaustive_four_by_four():
    assert len(ALLOWED) == 4
    assert all(len(actions) == 4 for actions in ALLOWED.values())


def test_resolve_still_enforces_the_note_rule_in_every_allowed_cell():
    for status in ("OPEN", "IN_PROGRESS"):
        ticket = ticket_in(status)
        with pytest.raises(ValidationError, match="resolution note"):
            ticket.resolve("")

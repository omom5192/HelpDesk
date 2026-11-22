"""The four ticket states and the lifecycle matrix.

Ticket is the context. Imports go one way: states -> base_state. Ticket is
only imported under TYPE_CHECKING to avoid a circular import.
"""

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from helpdesk.models.exceptions import InvalidTransitionError
from helpdesk.models.ticket_types import TicketStatus
from helpdesk.models.validators import validate_resolution_note
from helpdesk.patterns.state.base_state import REOPEN_WINDOW_DAYS, TicketState

if TYPE_CHECKING:
    from helpdesk.models.ticket import Ticket


class OpenState(TicketState):
    """A newly created ticket."""

    status_code = TicketStatus.OPEN
    display_name = "Open"

    def start_progress(self, ticket: "Ticket") -> None:
        from helpdesk.patterns.state.states import IN_PROGRESS_STATE

        ticket._transition_to(IN_PROGRESS_STATE)

    def resolve(self, ticket: "Ticket", note: str) -> None:
        from helpdesk.patterns.state.states import RESOLVED_STATE

        ticket.resolution_note = validate_resolution_note(note)
        ticket._transition_to(RESOLVED_STATE)

    def close(self, ticket: "Ticket", note: str = "") -> None:
        self._close_now(ticket)  # OPEN -> CLOSED (duplicate/spam)

    def reopen(self, ticket: "Ticket") -> None:
        raise InvalidTransitionError("Cannot reopen: the ticket is already open.")


class InProgressState(TicketState):
    """Someone is working on it."""

    status_code = TicketStatus.IN_PROGRESS
    display_name = "In Progress"

    def start_progress(self, ticket: "Ticket") -> None:
        raise InvalidTransitionError(
            "Cannot start progress: the ticket is already in progress."
        )

    def resolve(self, ticket: "Ticket", note: str) -> None:
        from helpdesk.patterns.state.states import RESOLVED_STATE

        ticket.resolution_note = validate_resolution_note(note)
        ticket._transition_to(RESOLVED_STATE)

    def close(self, ticket: "Ticket", note: str = "") -> None:
        raise InvalidTransitionError(
            "Cannot close: the ticket must be resolved first."
        )

    def reopen(self, ticket: "Ticket") -> None:
        raise InvalidTransitionError(
            "Cannot reopen: the ticket is in progress, not resolved/closed."
        )


class ResolvedState(TicketState):
    """Fix delivered, waiting to be closed."""

    status_code = TicketStatus.RESOLVED
    display_name = "Resolved"

    def start_progress(self, ticket: "Ticket") -> None:
        raise InvalidTransitionError(
            "Cannot start progress: the ticket is resolved; reopen it first."
        )

    def resolve(self, ticket: "Ticket", note: str) -> None:
        raise InvalidTransitionError("Cannot resolve: the ticket is already resolved.")

    def close(self, ticket: "Ticket", note: str = "") -> None:
        self._close_now(ticket)

    def reopen(self, ticket: "Ticket") -> None:
        self._reopen_to_progress(ticket)  # reporter says "not fixed"


class ClosedState(TicketState):
    """Terminal, except inside the 7-day reopen window."""

    status_code = TicketStatus.CLOSED
    display_name = "Closed"

    def start_progress(self, ticket: "Ticket") -> None:
        raise InvalidTransitionError("Cannot start progress: the ticket is closed.")

    def resolve(self, ticket: "Ticket", note: str) -> None:
        raise InvalidTransitionError("Cannot resolve: the ticket is closed.")

    def close(self, ticket: "Ticket", note: str = "") -> None:
        raise InvalidTransitionError("Cannot close: the ticket is already closed.")

    def reopen(self, ticket: "Ticket") -> None:
        if ticket.closed_at is None:
            raise InvalidTransitionError(
                "Ticket was closed without a timestamp; BR-2 window cannot be computed."
            )
        # Inclusive at exactly 7 days; a millisecond of scheduling jitter is
        # tolerated, one second over the boundary is refused.
        limit = timedelta(days=REOPEN_WINDOW_DAYS, milliseconds=1)
        if datetime.now(UTC) - ticket.closed_at > limit:
            raise InvalidTransitionError(
                f"Cannot reopen: the ticket was closed more than "
                f"{REOPEN_WINDOW_DAYS} days ago (reopen window expired)."
            )
        self._reopen_to_progress(ticket)


OPEN_STATE = OpenState()
IN_PROGRESS_STATE = InProgressState()
RESOLVED_STATE = ResolvedState()
CLOSED_STATE = ClosedState()

_STATES_BY_CODE = {
    state.status_code: state
    for state in (OPEN_STATE, IN_PROGRESS_STATE, RESOLVED_STATE, CLOSED_STATE)
}


def state_for(status_code: str) -> TicketState:
    """Rebuild a state from its stored code.

    Deliberate infrastructure mapping, NOT a Factory Method (no creator
    hierarchy, no product polymorphism).
    """
    try:
        return _STATES_BY_CODE[status_code]
    except KeyError:
        raise ValueError(f"Unknown ticket status code: {status_code!r}") from None

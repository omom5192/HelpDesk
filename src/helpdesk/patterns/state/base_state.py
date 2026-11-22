"""State pattern (GoF: Behavioral) - abstract state.

State: AbstractState (TicketState).

The lifecycle matrix (BR-1) lives ONLY in this package: each concrete state
implements either a real transition or a rejection raising
InvalidTransitionError with the reason. No other file branches on status.
"""

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import TYPE_CHECKING, ClassVar

REOPEN_WINDOW_DAYS: int = 7  # BR-2, inclusive at the boundary

if TYPE_CHECKING:
    from helpdesk.models.ticket import Ticket


class TicketState(ABC):
    """Stateless singletons; sharing the default instance is intentional."""

    status_code: ClassVar[str] = "?"
    display_name: ClassVar[str] = "Unknown"

    @abstractmethod
    def start_progress(self, ticket: "Ticket") -> None: ...

    @abstractmethod
    def resolve(self, ticket: "Ticket", note: str) -> None: ...

    @abstractmethod
    def close(self, ticket: "Ticket", note: str = "") -> None: ...

    @abstractmethod
    def reopen(self, ticket: "Ticket") -> None: ...

    # ---- shared helpers: local imports only (base must never import
    # states.py at module level - states.py imports this module) ----
    def _close_now(self, ticket: "Ticket") -> None:
        from helpdesk.patterns.state.states import CLOSED_STATE

        ticket.closed_at = datetime.now(UTC)
        ticket._transition_to(CLOSED_STATE)

    def _reopen_to_progress(self, ticket: "Ticket") -> None:
        from helpdesk.patterns.state.states import IN_PROGRESS_STATE

        ticket.closed_at = None
        # A reopen voids the old resolution (the reporter says "not fixed").
        ticket.resolution_note = None
        ticket._transition_to(IN_PROGRESS_STATE)

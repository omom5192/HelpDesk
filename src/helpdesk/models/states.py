"""Convenience re-exports of the State pattern for domain-layer consumers.

The implementation lives in ``helpdesk.patterns.state``; this module keeps
the import path used by audits and seeds stable.
"""

from helpdesk.patterns.state.base_state import REOPEN_WINDOW_DAYS, TicketState
from helpdesk.patterns.state.states import (
    CLOSED_STATE,
    IN_PROGRESS_STATE,
    OPEN_STATE,
    RESOLVED_STATE,
    ClosedState,
    InProgressState,
    OpenState,
    ResolvedState,
    state_for,
)

__all__ = [
    "REOPEN_WINDOW_DAYS",
    "TicketState",
    "OpenState",
    "InProgressState",
    "ResolvedState",
    "ClosedState",
    "OPEN_STATE",
    "IN_PROGRESS_STATE",
    "RESOLVED_STATE",
    "CLOSED_STATE",
    "state_for",
]

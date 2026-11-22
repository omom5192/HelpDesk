"""Ticket ordering policies.

TicketService holds one of these and calls order() when listing tickets.
Sorting returns a new list; the input is never changed.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import TYPE_CHECKING

_PRIORITY_RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

if TYPE_CHECKING:
    from helpdesk.models.ticket import Ticket


def _priority_key(priority: str) -> int:
    try:
        return _PRIORITY_RANK[priority]
    except KeyError:
        raise ValueError(f"Unknown priority value: {priority!r}") from None


def _as_utc(value: datetime) -> datetime:
    """Never compare naive against aware datetimes (that raises TypeError)."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


class TicketOrderingStrategy(ABC):
    """Common interface for ordering policies."""

    @abstractmethod
    def order(self, tickets: "Sequence[Ticket]") -> "list[Ticket]":
        """Return the tickets ordered by this policy; input list untouched."""


class PriorityOrderingStrategy(TicketOrderingStrategy):
    """CRITICAL first, oldest first inside a priority (BR-4)."""

    def order(self, tickets: "Sequence[Ticket]") -> "list[Ticket]":
        return sorted(
            tickets,
            key=lambda ticket: (
                _priority_key(ticket.priority),
                _as_utc(ticket.created_at or datetime.now(UTC)),
            ),
        )


class DeadlineOrderingStrategy(TicketOrderingStrategy):
    """Earliest deadline first, tickets without one last (BR-5)."""

    def order(self, tickets: "Sequence[Ticket]") -> "list[Ticket]":
        def key(ticket: "Ticket") -> tuple:
            rank = _priority_key(ticket.priority)
            created = _as_utc(ticket.created_at or datetime.now(UTC))
            if ticket.deadline is None:
                return (1, 0, rank, created)
            return (0, _as_utc(ticket.deadline).timestamp(), rank, created)

        return sorted(tickets, key=key)

"""Strategy: ticket ordering policies.

Strategy: AbstractStrategy -> TicketOrderingStrategy
Strategy: ConcreteStrategy -> PriorityOrderingStrategy (BR-4)
Strategy: ConcreteStrategy -> DeadlineOrderingStrategy (BR-5)
Context: services.ticket_service receives strategies through this common
interface and switches them at runtime (FR-10). Strategies return a NEW
sorted list and never mutate their input.
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
    """Strategy: AbstractStrategy."""

    @abstractmethod
    def order(self, tickets: "Sequence[Ticket]") -> "list[Ticket]":
        """Return the tickets ordered by this policy; input list untouched."""


class PriorityOrderingStrategy(TicketOrderingStrategy):
    """Strategy: ConcreteStrategy - CRITICAL>HIGH>MEDIUM>LOW, older first (BR-4)."""

    def order(self, tickets: "Sequence[Ticket]") -> "list[Ticket]":
        return sorted(
            tickets,
            key=lambda ticket: (
                _priority_key(ticket.priority),
                _as_utc(ticket.created_at or datetime.now(UTC)),
            ),
        )


class DeadlineOrderingStrategy(TicketOrderingStrategy):
    """Strategy: ConcreteStrategy - earliest deadline first, nulls last (BR-5)."""

    def order(self, tickets: "Sequence[Ticket]") -> "list[Ticket]":
        def key(ticket: "Ticket") -> tuple:
            rank = _priority_key(ticket.priority)
            created = _as_utc(ticket.created_at or datetime.now(UTC))
            if ticket.deadline is None:
                return (1, 0, rank, created)
            return (0, _as_utc(ticket.deadline).timestamp(), rank, created)

        return sorted(tickets, key=key)

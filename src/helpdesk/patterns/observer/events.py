"""Immutable ticket domain events published through the Observer pattern."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TicketEvent:
    """Base class for every ticket event."""

    ticket_id: int
    occurred_at: datetime

    @property
    def name(self) -> str:
        return type(self).__name__

    @property
    def description(self) -> str:
        """Human-readable summary; subclasses override with specifics."""
        return f"{self.name} on ticket #{self.ticket_id}"


@dataclass(frozen=True)
class TicketCreated(TicketEvent):
    title: str
    category: str
    priority: str

    @property
    def description(self) -> str:
        return f"Ticket '{self.title}' created [{self.category}/{self.priority}]"


@dataclass(frozen=True)
class TicketAssigned(TicketEvent):
    staff_id: int

    @property
    def description(self) -> str:
        return f"Assigned to staff #{self.staff_id}"


@dataclass(frozen=True)
class TicketStatusChanged(TicketEvent):
    old_status: str
    new_status: str

    @property
    def description(self) -> str:
        return f"Status changed {self.old_status} -> {self.new_status}"

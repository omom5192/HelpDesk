"""Immutable ticket domain events published through the Observer pattern.

Every event carries a ``message``: the human-readable notification text.
It defaults to the event's ``description`` and may be overridden (e.g. by
UrgentNotificationDecorator via ``dataclasses.replace``) without mutating
the original event.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class TicketEvent:
    """Base class for every ticket event."""

    ticket_id: int
    occurred_at: datetime
    # kw_only keeps subclasses free to declare required positional fields.
    message: str = field(default="", kw_only=True)

    def __post_init__(self) -> None:
        if not self.message:
            # frozen dataclass: assign through object.__setattr__ once, at init.
            object.__setattr__(self, "message", self.description)

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

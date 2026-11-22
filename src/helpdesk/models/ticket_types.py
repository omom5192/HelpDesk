"""Ticket value sets (requirements BR-9)."""

from enum import StrEnum


class TicketCategory(StrEnum):
    TECHNICAL = "TECHNICAL"
    ACCOUNT = "ACCOUNT"
    HARDWARE = "HARDWARE"


class TicketPriority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TicketStatus(StrEnum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


TICKET_CATEGORIES: tuple[str, ...] = tuple(t.value for t in TicketCategory)
TICKET_PRIORITIES: tuple[str, ...] = tuple(t.value for t in TicketPriority)
TICKET_STATUSES: tuple[str, ...] = tuple(t.value for t in TicketStatus)

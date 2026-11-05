"""Canonical ticket enums — Decision A, approved by the team.

Enum values are the exact uppercase strings the frozen schema CHECK
stores, so model -> database needs no translation. Lenient casing
("hardware", "Hardware") is accepted at the validators layer, which
canonicalizes to these tokens; storage only ever sees these values.
"""

from enum import Enum


class TicketPriority(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TicketCategory(Enum):
    TECHNICAL = "TECHNICAL"
    ACCOUNT = "ACCOUNT"
    HARDWARE = "HARDWARE"

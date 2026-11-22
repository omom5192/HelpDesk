"""Factory Method (GoF: Creational) - abstract creator.

Factory Method: AbstractCreator (TicketCreator).

One creator per category knows: (a) the category-specific mandatory fields
and their validation, (b) the default priority when the caller does not
choose one, (c) the concrete Product class to instantiate (BR-6).
"""

from abc import ABC, abstractmethod
from datetime import datetime
import re
from typing import TYPE_CHECKING

from helpdesk.models.exceptions import ValidationError
from helpdesk.models.ticket_types import TicketCategory, TicketPriority

if TYPE_CHECKING:
    from helpdesk.models.ticket import Ticket

TECHNICAL_COMPONENTS: tuple[str, ...] = (
    "network",
    "email",
    "operating_system",
    "database",
    "hardware_driver",
    "printer",
)
ACCOUNT_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
_ACCOUNT_PATTERN = ACCOUNT_PATTERN  # compatibility with the frozen contract name
_ASSET_TAG_PATTERN = re.compile(r"^PC-\d{4}$")

_DEFAULT_PRIORITY: dict[str, str] = {
    TicketCategory.TECHNICAL: TicketPriority.MEDIUM,
    TicketCategory.ACCOUNT: TicketPriority.HIGH,
    TicketCategory.HARDWARE: TicketPriority.LOW,
}


class TicketCreator(ABC):
    """Factory Method: Creator - declares the factory method."""

    category: str = ""
    default_priority: str = TicketPriority.MEDIUM

    @abstractmethod
    def create(
        self,
        *,
        title: str,
        description: str,
        deadline: datetime | None,
        created_at: datetime,
        **category_fields,
    ) -> "Ticket":
        """Build a validated product; the service owns the clock."""

    def _validate_category(self, value: str) -> str:
        canonical = (value or "").strip().upper()
        if canonical not in TicketCategory.__members__:
            raise ValidationError(
                f"Category must be one of: {', '.join(TicketCategory.__members__)}"
            )
        return canonical

    def _require(self, field_name: str, value: str | None, rule: str = "provided") -> str:
        """Mandatory category field helper: fails with the rule text."""
        if value is None or not value.strip():
            raise ValidationError(
                f"'{field_name}' is required for {self.category} tickets ({rule})"
            )
        return value.strip()

    def _apply_default_priority(self, priority: str | None) -> str:
        return priority or self.default_priority

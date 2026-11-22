"""Creator for HARDWARE tickets."""

from datetime import datetime
from typing import TYPE_CHECKING

from helpdesk.models.exceptions import ValidationError
from helpdesk.models.ticket import HardwareTicket
from helpdesk.models.ticket_types import TicketPriority
from helpdesk.models.validators import (
    validate_description,
    validate_priority,
    validate_title,
)
from helpdesk.patterns.factory.abstract_creator import (
    _ASSET_TAG_PATTERN,
    TicketCreator,
)

if TYPE_CHECKING:
    from helpdesk.models.ticket import Ticket


class HardwareTicketCreator(TicketCreator):
    """Builds a HardwareTicket with tag and location."""

    category = "HARDWARE"
    default_priority = TicketPriority.LOW

    def _asset_tag(self, value: str | None) -> str:
        value = self._require("asset_tag", value, rule="format PC-1234")
        tag = value.strip().upper()
        if not _ASSET_TAG_PATTERN.fullmatch(tag):
            raise ValidationError("asset_tag must match ^PC-\\d{4}$ (e.g. PC-1234).")
        return tag

    def _location(self, value: str | None) -> str:
        return self._require("location", value, rule="room/building text")

    def create(
        self,
        *,
        title: str,
        description: str,
        deadline: datetime | None,
        created_at: datetime,
        priority: str | None = None,
        asset_tag: str | None = None,
        location: str | None = None,
    ) -> "Ticket":
        tag = self._asset_tag(asset_tag)
        location = self._location(location)
        return HardwareTicket(
            title=validate_title(title),
            description=validate_description(description),
            category=self.category,
            priority=validate_priority(priority or self.default_priority),
            deadline=deadline,
            created_at=created_at,
            updated_at=created_at,
            asset_tag=tag,
            location=location,
        )

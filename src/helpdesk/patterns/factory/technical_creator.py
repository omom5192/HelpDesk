"""Creator for TECHNICAL tickets."""

from datetime import datetime
from typing import TYPE_CHECKING

from helpdesk.models.exceptions import ValidationError
from helpdesk.models.ticket import TechnicalTicket
from helpdesk.models.ticket_types import TicketPriority
from helpdesk.models.validators import (
    validate_description,
    validate_priority,
    validate_title,
)
from helpdesk.patterns.factory.abstract_creator import (
    TECHNICAL_COMPONENTS,
    TicketCreator,
)

if TYPE_CHECKING:
    from helpdesk.models.ticket import Ticket


class TechnicalTicketCreator(TicketCreator):
    """Builds a TechnicalTicket with a validated component."""

    category = "TECHNICAL"
    default_priority = TicketPriority.MEDIUM

    def _component(self, value: str | None) -> str:
        value = self._require("component", value, rule="network/email/...")
        canonical = value.strip().lower()
        if canonical not in TECHNICAL_COMPONENTS:
            raise ValidationError(
                f"Component '{value}' is unknown. "
                f"Allowed: {', '.join(TECHNICAL_COMPONENTS)}"
            )
        return canonical

    def create(
        self,
        *,
        title: str,
        description: str,
        deadline: datetime | None,
        created_at: datetime,
        priority: str | None = None,
        component: str | None = None,
    ) -> "Ticket":
        component = self._component(component)
        return TechnicalTicket(
            title=validate_title(title),
            description=validate_description(description),
            category=self.category,
            priority=validate_priority(priority or self.default_priority),
            deadline=deadline,
            created_at=created_at,
            updated_at=created_at,
            technical_component=component,
        )

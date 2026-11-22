"""Creator for ACCOUNT tickets."""

from datetime import datetime
from typing import TYPE_CHECKING

from helpdesk.models.exceptions import ValidationError
from helpdesk.models.ticket import AccountTicket
from helpdesk.models.ticket_types import TicketPriority
from helpdesk.models.validators import (
    validate_description,
    validate_priority,
    validate_title,
)
from helpdesk.patterns.factory.abstract_creator import ACCOUNT_PATTERN, TicketCreator

if TYPE_CHECKING:
    from helpdesk.models.ticket import Ticket


class AccountTicketCreator(TicketCreator):
    """Builds an AccountTicket with the required account field."""

    category = "ACCOUNT"
    default_priority = TicketPriority.HIGH

    def _affected_account(self, value: str | None) -> str:
        value = self._require("affected_account", value, rule="username pattern")
        if not ACCOUNT_PATTERN.fullmatch(value):
            raise ValidationError(
                "affected_account must match the username pattern "
                "(letters, digits, dot/underscore/dash)."
            )
        return value

    def create(
        self,
        *,
        title: str,
        description: str,
        deadline: datetime | None,
        created_at: datetime,
        priority: str | None = None,
        affected_account: str | None = None,
    ) -> "Ticket":
        account = self._affected_account(affected_account)
        return AccountTicket(
            title=validate_title(title),
            description=validate_description(description),
            category=self.category,
            priority=validate_priority(priority or self.default_priority),
            deadline=deadline,
            created_at=created_at,
            updated_at=created_at,
            affected_account=account,
        )

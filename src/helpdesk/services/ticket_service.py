"""TicketService - application use cases.

The service owns the clock (contract amendment #1) and wires the Factory
Method registry and the ordering Strategy. Concrete creators/strategies are
named only here and in the composition root, never in the domain layer.
"""

from datetime import UTC, datetime

from helpdesk.models.exceptions import InvalidTicketTypeError
from helpdesk.models.ticket import Ticket
from helpdesk.patterns.factory import CREATOR_REGISTRY
from helpdesk.patterns.observer.events import TicketCreated, TicketStatusChanged
from helpdesk.patterns.observer.publisher import TicketEventPublisher
from helpdesk.patterns.strategy.ordering_strategies import (
    PriorityOrderingStrategy,
    TicketOrderingStrategy,
)
from helpdesk.repositories.staff_repository import StaffRepository
from helpdesk.repositories.ticket_repository import TicketRepository

class TicketService:
    def __init__(
        self,
        ticket_repository: TicketRepository,
        staff_repository: StaffRepository,
        publisher: TicketEventPublisher,
    ) -> None:
        self._tickets = ticket_repository
        self._staff = staff_repository
        self._events = publisher
        # One ordering policy at a time; see FR-10.
        self._ordering: TicketOrderingStrategy = PriorityOrderingStrategy()

    def set_ordering_strategy(self, strategy: TicketOrderingStrategy) -> None:
        """Runtime switch point - any ordering policy behind one interface."""
        if not isinstance(strategy, TicketOrderingStrategy):
            raise TypeError("strategy must implement TicketOrderingStrategy")
        self._ordering = strategy

    def create_ticket(
        self,
        *,
        title: str,
        description: str,
        category: str,
        priority: str | None = None,
        deadline: datetime | None = None,
        **category_fields,
    ) -> Ticket:
        """Create through the category creator, persist, and notify."""
        creator = CREATOR_REGISTRY.get((category or "").strip().upper())
        if creator is None:
            raise InvalidTicketTypeError(
                f"Category must be one of: {', '.join(sorted(CREATOR_REGISTRY))}"
            )

        now = datetime.now(UTC)  # amendment #1: the service owns the clock
        ticket = creator.create(
            title=title,
            description=description,
            deadline=deadline,
            created_at=now,
            priority=priority,
            **category_fields,
        )

        self._tickets.save(ticket)
        self._events.publish(
            TicketCreated(
                ticket_id=ticket.id,
                occurred_at=now,
                title=ticket.title,
                category=ticket.category,
                priority=ticket.priority,
            )
        )
        return ticket

    def get_ticket(self, ticket_id: int) -> Ticket:
        return self._tickets.get(ticket_id)

    def list_tickets(
        self,
        *,
        status=None,
        priority=None,
        category=None,
        staff_id=None,
    ) -> list[Ticket]:
        found = self._tickets.find(
            status=status,
            priority=priority,
            category=category,
            staff_id=staff_id,
        )
        return self._ordering.order(found)

    def transition(self, ticket_id: int, action: str, note: str = "") -> Ticket:
        """Execute a lifecycle action through the State context (BR-1)."""
        ticket = self._tickets.get(ticket_id)
        old_status = ticket.status_code
        ticket.transition(action, note=note)
        self._tickets.save(ticket)
        self._events.publish(
            TicketStatusChanged(
                ticket_id=ticket.id,
                occurred_at=ticket.updated_at or datetime.now(UTC),
                old_status=old_status,
                new_status=ticket.status_code,
            )
        )
        return ticket

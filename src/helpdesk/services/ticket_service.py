"""Ticket service: application use cases for creating and retrieving tickets."""

from datetime import UTC, datetime

from helpdesk.models.ticket import Ticket
from helpdesk.models.validators import (
    validate_category,
    validate_priority,
    validate_ticket_data,
)
from helpdesk.patterns.observer.events import TicketCreated
from helpdesk.patterns.observer.publisher import TicketEventPublisher
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

    def create_ticket(
        self,
        *,
        title: str,
        description: str,
        category: str,
        priority: str = "MEDIUM",
        deadline=None,
    ) -> Ticket:
        validate_ticket_data(
            title=title,
            description=description,
            priority=priority,
            category=category,
        )
        category = validate_category(category)
        priority = validate_priority(priority)
        now = datetime.now(UTC)

        # TODO for Week 2: replace this with the Factory Method creator.
        ticket = Ticket(
            title=title,
            description=description,
            category=category,
            priority=priority,
            created_at=now,
            updated_at=now,
            deadline=deadline,
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
    ) -> list:
        return self._tickets.find(
            status=status,
            priority=priority,
            category=category,
            staff_id=staff_id,
        )

<<<<<<< HEAD
from helpdesk.repositories.repository import TicketRepository

class TicketService:
    def __init__(self, db_path="helpdesk.db"):
        self.repository = TicketRepository(db_path=db_path)

    def create_new_ticket(self, title: str, description: str, priority: str = "MEDIUM", category: str = "GENERAL"):
        if not title or not title.strip():
            raise ValueError("Baslik alani bos birakilamaz.")
        
        if not description or not description.strip():
            raise ValueError("Aciklama alani bos birakilamaz.")

        ticket_id = self.repository.add_ticket(
            title=title.strip(),
            description=description.strip(),
            priority=priority,
            category=category
        )
        return ticket_id

    def update_ticket_status(self, ticket_id: int, new_status: str):
        valid_statuses = ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"]
        status_upper = new_status.upper()
        
        if status_upper not in valid_statuses:
            raise ValueError(f"Gecersiz durum. Gecerli durumlar: {valid_statuses}")

        ticket = self.get_ticket_by_id(ticket_id)
        if not ticket:
            raise ValueError("Boyle bir bilet bulunamadi.")

        self.repository.update_status(ticket_id, status_upper)
        return True

    def get_all_system_tickets(self):
        return self.repository.get_all_tickets()


    def get_ticket_by_id(self, ticket_id: int):
        tickets = self.repository.get_all_tickets()
        for ticket in tickets:
            if ticket.get("id") == ticket_id:
                return ticket
        return None
=======
"""Ticket service: application use cases for creating and retrieving tickets."""

from datetime import datetime, timezone

from helpdesk.models.ticket import Ticket
from helpdesk.models.validators import validate_category, validate_priority
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
        category = validate_category(category)
        priority = validate_priority(priority)
        now = datetime.now(timezone.utc)

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
>>>>>>> d6f5ce911c39ccb1cb20d24fecdc72beb2b8212c

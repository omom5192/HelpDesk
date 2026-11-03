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
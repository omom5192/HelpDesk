
class Ticket:
    """Represent a HelpDesk support ticket."""

    ALLOWED_STATUSES = ("Open", "In Progress", "Resolved", "Closed")

    def __init__(
        self,
        ticket_id: int,
        title: str,
        description: str,
        priority: str = "Medium",
    ) -> None:
        self.ticket_id = ticket_id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = "Open"

    def update_status(self, new_status: str) -> bool:
        """Update the ticket status if it is valid."""
        if new_status not in self.ALLOWED_STATUSES:
            print(
                f"Geçersiz durum! "
                f"Kullanılabilir durumlar: {list(self.ALLOWED_STATUSES)}"
            )
            return False

        self.status = new_status
        print(
            f"Bilet #{self.ticket_id} durumu güncellendi: {self.status}"
        )
        return True

    def get_details(self) -> dict:
        """Return the ticket details as a dictionary."""
        return {
            "ID": self.ticket_id,
            "Title": self.title,
            "Description": self.description,
            "Priority": self.priority,
            "Status": self.status,
        }

"""Domain model of a ticket — the frozen schema's columns as one class.

Category-specific fields stay optional columns (technical_component,
affected_account, asset_tag, location). Status tokens are the uppercase
ones the schema CHECK allows; transition logic belongs to the State
pattern (M2's milestone), not here.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Ticket:
    id: int | None = None
    title: str = ""
    description: str = ""
    category: str = ""
    priority: str = "MEDIUM"
    status: str = "OPEN"
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deadline: datetime | None = None
    assigned_staff_id: int | None = None
    technical_component: str | None = None
    affected_account: str | None = None
    asset_tag: str | None = None
    location: str | None = None
    closed_at: datetime | None = None
    resolution_note: str | None = None

    @property
    def status_code(self) -> str:
        """Uppercase status token — what the CLI prints."""
        return self.status

    def get_details(self) -> dict:
        """Field -> value map for the console 'View' screen."""
        return {
            "ID": self.id,
            "Title": self.title,
            "Description": self.description,
            "Category": self.category,
            "Priority": self.priority,
            "Status": self.status,
            "Created": self.created_at,
            "Updated": self.updated_at,
            "Deadline": self.deadline,
            "Assigned staff": self.assigned_staff_id,
            "Closed": self.closed_at,
            "Resolution note": self.resolution_note,
        }

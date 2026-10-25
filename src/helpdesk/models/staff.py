"""support staff model"""
from dataclasses import dataclass
from datetime import datetime

from helpdesk.models.exceptions import ValidattionError


@dataclass
class Staff:
    id: int | None = None
    full_name: str = ""
    role: str = "SUPPORT"
    created_at:  datetime | None = None

    def __post_init__(self) -> None:
        if not self.full_name.strip():
            raise ValidattionError("staff full_name mus'nt be empty.")
        self.full_name = self.full_name.strip()

"""Ticket aggregate - Context of the State pattern and Factory Method Product.

The shared base carries every schema column so one table and one repository
round-trip serve all three categories; product subclasses add behavior only.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
import re

from helpdesk.models.validators import validate_description, validate_title
from helpdesk.patterns.state.base_state import TicketState
from helpdesk.patterns.state.states import CLOSED_STATE, OPEN_STATE, state_for


@dataclass
class Ticket:
    id: int | None = None  # DB assigns; None until saved
    title: str = ""
    description: str = ""
    category: str = ""
    priority: str = "MEDIUM"
    deadline: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    assigned_staff_id: int | None = None
    technical_component: str | None = None  # TECHNICAL
    affected_account: str | None = None  # ACCOUNT
    asset_tag: str | None = None  # HARDWARE
    location: str | None = None  # HARDWARE
    closed_at: datetime | None = None
    resolution_note: str | None = None
    # One state object per status is enough - the states have no data of
    # their own, so sharing the instance is fine.
    state: TicketState = OPEN_STATE

    def __post_init__(self) -> None:
        self.title = validate_title(self.title)
        self.description = validate_description(self.description)

    # ---- lifecycle: the Context delegates decisions to the current State ----
    def start_progress(self) -> None:
        self.state.start_progress(self)

    def resolve(self, note: str) -> None:
        self.state.resolve(self, note)

    def close(self, note: str = "") -> None:
        self.state.close(self, note)

    def reopen(self) -> None:
        self.state.reopen(self)

    def transition(self, action: str, note: str = "") -> None:
        """Adapter used by the service/CLI: map an action token to a state call."""
        token = (action or "").strip().upper()
        if token in ("IN_PROGRESS", "START_PROGRESS", "START"):
            self.start_progress()
        elif token in ("RESOLVED", "RESOLVE"):
            self.resolve(note)
        elif token in ("CLOSED", "CLOSE"):
            self.close(note or "")
        elif token in ("REOPEN", "OPEN"):
            if self.status_code == "OPEN":
                self.reopen()  # produces the documented "already open" reason
            else:
                self.reopen()
        else:
            from helpdesk.models.exceptions import InvalidTransitionError

            raise InvalidTransitionError(f"Unknown transition action: {action!r}")

    @property
    def status_code(self) -> str:
        """Uppercase token stored in the database."""
        return str(self.state.status_code)

    @property
    def status(self) -> str:
        """Alias of ``status_code`` kept for callers that read ``ticket.status``."""
        return self.status_code

    @property
    def status_display(self) -> str:
        """Human-readable status name for the console."""
        return self.state.display_name

    def assign(self, staff_id: int) -> None:
        """Attach a staff member; BR-7 is enforced by AssignmentService."""
        self.assigned_staff_id = staff_id

    def get_details(self) -> dict:
        """Field -> value map for the console 'View' screen."""
        return {
            "ID": self.id,
            "Title": self.title,
            "Description": self.description,
            "Category": self.category,
            "Priority": self.priority,
            "Status": self.status_code,
            "Deadline": self.deadline,
            "Assigned staff": self.assigned_staff_id,
            "Closed": self.closed_at,
            "Resolution note": self.resolution_note,
        }

    # ---- internals: callable ONLY by state objects ----
    def _transition_to(self, next_state: TicketState) -> None:
        self.state = next_state
        self.updated_at = datetime.now(UTC)

    def set_state_from_code(self, status_code: str) -> None:
        """Rebuild the state during hydration (infrastructure mapping)."""
        self.state = state_for(status_code)


# --- concrete ticket types ---------------------------------------------
# ConcreteProducts (Week 2). Category-specific rules from BR-6 live here.

_TECHNICAL_COMPONENTS: tuple[str, ...] = (
    "network",
    "email",
    "operating_system",
    "database",
    "hardware_driver",
    "printer",
)


class TechnicalTicket(Ticket):
    """Technical ticket: component-based escalation."""

    @property
    def component(self) -> str | None:
        return self.technical_component

    def escalation_level(self) -> tuple[str, ...]:
        """Component-driven escalation ladder (BR-6 behavior, simulated)."""
        ladder = {
            "database": ("DATABASE_ADMIN", "INFRASTRUCTURE_LEAD"),
            "network": ("NETWORK_ADMIN",),
            "email": ("POSTMASTER",),
        }
        return ladder.get(self.technical_component or "", ())


class AccountTicket(Ticket):
    """Account ticket: identity and login issues."""

    def is_lockout(self) -> bool:
        """Word-boundary match avoids the 'unblocked' false positive."""
        text = f"{self.resolution_note or ''} {self.description or ''}"
        return bool(re.search(r"\b(locked|password)\b", text, flags=re.IGNORECASE))


class HardwareTicket(Ticket):
    """Hardware ticket: physical asset issues."""

    def is_warranty_eligible(self) -> bool:
        """Documented stand-in: a deterministic policy until a real field exists."""
        if self.asset_tag is None or self.created_at is None:
            return False
        return (self.created_at.year % 9) != 0

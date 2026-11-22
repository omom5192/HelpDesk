"""Deterministic demo seed for HelpDesk (M1 - Week 3).

- IDEMPOTENT: refuses to run if staff already exist - a seed that edits
  history is a bug machine; delete the DB file to reset.
- DETERMINISTIC: fixed FAKE_NOW for created/updated/deadlines; the two
  BR-2 demo tickets use wall-clock offsets so the 7-day window works on
  any demo date.
- Layer discipline: talks only to the repositories. No sqlite3 here.

Run: python -m helpdesk.database.seed
"""

from datetime import UTC, datetime, timedelta

from helpdesk.database.database import Database
from helpdesk.models.staff import Staff
from helpdesk.models.states import state_for
from helpdesk.models.ticket import AccountTicket, HardwareTicket, TechnicalTicket
from helpdesk.repositories.staff_repository import StaffRepository
from helpdesk.repositories.ticket_repository import TicketRepository

FAKE_NOW = datetime(2026, 11, 2, 9, 0, tzinfo=UTC)
_DB_PATH = "helpdesk.db"

_NAMES = [
    ("Dana Nasser", "first_line"),
    ("Hadi Saleh", "network"),
    ("Lina Faris", "email"),
    ("Omar Kassab", "accounts"),
    ("Rima Aziz", "hardware"),
    ("Basel Samir", "dba"),
]


def _staff() -> list[Staff]:
    return [
        Staff(
            full_name=name,
            role=role,
            created_at=FAKE_NOW - timedelta(days=6 - index),
        )
        for index, (name, role) in enumerate(_NAMES)
    ]


def _ticket(cls, *, category, title, description, priority, age_days, status,
            deadline_days=None, assigned=None, note=None, closed_ago=None,
            **category_fields):
    """Shared base columns let one builder fit all three product classes."""
    created = FAKE_NOW - timedelta(days=age_days)
    touched = (
        datetime.now(UTC) - timedelta(days=closed_ago)
        if closed_ago is not None
        else created
    )
    deadline = (
        FAKE_NOW + timedelta(days=deadline_days)
        if deadline_days is not None
        else None
    )
    return cls(
        title=title,
        description=description,
        category=category,
        priority=priority,
        created_at=created,
        updated_at=touched,
        deadline=deadline,
        state=state_for(status),
        resolution_note=note,
        closed_at=touched if closed_ago is not None else None,
        assigned_staff_id=assigned,
        **category_fields,
    )


def _tickets() -> list:
    # BR-8 workload design: s1=2, s2=2, s3=1, s4=1, s5=0, s6=0.
    # Two AUTO assignments therefore pick staff 5, then staff 6.
    return [
        _ticket(TechnicalTicket, category="TECHNICAL", title="Mail server queue stuck",
                description="Outbound SMTP queue has not drained since the morning.",
                priority="CRITICAL", age_days=2, status="OPEN",
                deadline_days=1, assigned=1, technical_component="email"),
        _ticket(TechnicalTicket, category="TECHNICAL", title="Lab VLAN drops packets",
                description="Classroom lab network loses packet bursts every few minutes.",
                priority="HIGH", age_days=1, status="OPEN",
                deadline_days=4, assigned=1, technical_component="network"),
        _ticket(AccountTicket, category="ACCOUNT", title="Registrar account expired",
                description="Staff account expired mid-semester and cannot be renewed.",
                priority="MEDIUM", age_days=4, status="OPEN", assigned=2,
                affected_account="registrar.office"),
        _ticket(TechnicalTicket, category="TECHNICAL", title="Student DB deadlock storm",
                description="Finance reporting queries deadlock under load spikes.",
                priority="HIGH", age_days=3, status="IN_PROGRESS", assigned=2,
                technical_component="database"),
        _ticket(HardwareTicket, category="HARDWARE", title="Projector flickers",
                description="Auditorium beam projector flickers at full brightness.",
                priority="MEDIUM", age_days=5, status="OPEN", assigned=3,
                asset_tag="PC-1004", location="Auditorium A"),
        _ticket(AccountTicket, category="ACCOUNT", title="Lockout after five failures",
                description="User is locked out after five failed password attempts.",
                priority="HIGH", age_days=2, status="OPEN", assigned=4,
                affected_account="s2026001"),
        _ticket(TechnicalTicket, category="TECHNICAL", title="Printer driver update",
                description="Operating system update removed the print driver entirely.",
                priority="LOW", age_days=1, status="OPEN",
                technical_component="printer"),
        _ticket(TechnicalTicket, category="TECHNICAL", title="DNS resolution delay",
                description="Campus DNS answers take seconds at peak times.",
                priority="MEDIUM", age_days=6, status="OPEN",
                technical_component="network"),
        _ticket(AccountTicket, category="ACCOUNT", title="Course portal access",
                description="Joined mid-term and needs the portal account today.",
                priority="MEDIUM", age_days=6, status="RESOLVED", assigned=3,
                affected_account="s2026777", note="Access granted and documented"),
        # BR-2 demo A: closed 2 days ago -> REOPEN allowed.
        _ticket(TechnicalTicket, category="TECHNICAL", title="Outage came back",
                description="Email outage returned after the earlier closure.",
                priority="CRITICAL", age_days=5, status="CLOSED", assigned=1,
                technical_component="email", note="Closed after temporary fix",
                closed_ago=2),
        # BR-2 demo B: closed 10 days ago -> REOPEN refused.
        _ticket(HardwareTicket, category="HARDWARE", title="Dead dock station",
                description="Docking station does not power on since the move.",
                priority="HIGH", age_days=12, status="CLOSED", assigned=4,
                asset_tag="PC-1100", location="Lab 3", note="Replaced under warranty",
                closed_ago=10),
    ]


def seed(db: Database) -> dict[str, int]:
    """Populate demo data; returns {'staff': n, 'tickets': n}."""
    staff_repo = StaffRepository(db)
    if staff_repo.list_all():
        print("[seed] database already contains staff - refusing to duplicate.")
        return {"staff": 0, "tickets": 0}

    for person in _staff():  # insert order == id order (1..6)
        staff_repo.save(person)

    ticket_repo = TicketRepository(db)
    tickets = _tickets()
    for ticket in tickets:
        ticket_repo.save(ticket)

    print(
        f"[seed] seeded 6 staff and {len(tickets)} tickets "
        f"(FAKE_NOW={FAKE_NOW:%Y-%m-%d %H:%M}Z)."
    )
    return {"staff": 6, "tickets": len(tickets)}


def main() -> None:
    db = Database(_DB_PATH)
    db.initialize()
    seed(db)


if __name__ == "__main__":
    main()

"""AssignmentService - dispatch policy as a Strategy context (Week 2).

Strategy: Context -> this service (like TicketService for ordering).

BR-7: assign only in OPEN or IN_PROGRESS.
BR-8: workload = OPEN + IN_PROGRESS tickets; AUTO assignment picks the
fewest-loaded candidate through the AssignmentStrategy (M1's code).
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from helpdesk.database.database import Database
from helpdesk.models.exceptions import DomainError
from helpdesk.patterns.observer.events import TicketEvent
from helpdesk.patterns.observer.publisher import TicketEventPublisher
from helpdesk.patterns.strategy.assignment_strategies import (
    AssignmentStrategy,
    FewestOpenTicketsStrategy,
)
from helpdesk.repositories.staff_repository import StaffRepository
from helpdesk.repositories.ticket_repository import TicketRepository

if TYPE_CHECKING:
    from helpdesk.models.ticket import Ticket

_ASSIGNABLE_STATES = ("OPEN", "IN_PROGRESS")


@dataclass(frozen=True)
class StaffAssignedEvent(TicketEvent):
    """Observer event: a ticket received a staff member."""

    staff_id: int

    @property
    def description(self) -> str:
        return f"Ticket #{self.ticket_id} assigned to staff #{self.staff_id}"


StaffAssigned = StaffAssignedEvent


class AssignmentService:
    """Strategy: Context - holds one AssignmentStrategy, hot-swappable."""

    def __init__(
        self,
        db: Database,
        publisher: TicketEventPublisher | None = None,
        strategy: AssignmentStrategy | None = None,
        ticket_repository: TicketRepository | None = None,
        staff_repository: StaffRepository | None = None,
    ) -> None:
        self._tickets = ticket_repository or TicketRepository(db)
        self._staff = staff_repository or StaffRepository(db)
        self._publisher = publisher
        self._strategy: AssignmentStrategy = strategy or FewestOpenTicketsStrategy()

    def set_assignment_strategy(self, strategy: AssignmentStrategy) -> None:
        if not isinstance(strategy, AssignmentStrategy):
            raise TypeError("strategy must implement AssignmentStrategy")
        self._strategy = strategy

    def candidate_overview(self) -> list[tuple[int, str, int]]:
        """(id, name, open workload) for the CLI/demos."""
        return [
            (
                staff.id,
                staff.name,
                int(self._staff.count_open_workloads(staff.id)),
            )
            for staff in self._staff.list_all()
        ]

    def assign(self, ticket_id: int, staff_id: int | None = None) -> "Ticket":
        ticket = self._tickets.get(ticket_id)

        if ticket.status_code not in _ASSIGNABLE_STATES:
            raise DomainError(
                f"Ticket status is {ticket.status_code}; BR-7 allows assignment "
                f"only in {', '.join(_ASSIGNABLE_STATES)}."
            )

        if staff_id is None:  # AUTO - fire through the Strategy
            staff = self._staff.list_all()
            staff_id = self._strategy.select(
                [member.id for member in staff],
                {
                    member.id: int(self._staff.count_open_workloads(member.id))
                    for member in staff
                },
            )
        else:
            self._staff.get(staff_id)  # explicit choice must exist

        ticket.assign(staff_id)
        self._tickets.save(ticket)

        if self._publisher is not None:
            self._publisher.publish(
                StaffAssignedEvent(
                    ticket_id=ticket.id,
                    occurred_at=datetime.now(UTC),
                    staff_id=staff_id,
                )
            )
        return ticket

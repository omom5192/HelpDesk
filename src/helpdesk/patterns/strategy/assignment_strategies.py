"""Strategy: staff-assignment policies.

Strategy: AbstractStrategy -> AssignmentStrategy
Strategy: ConcreteStrategy -> FewestOpenTicketsStrategy (BR-8)
Context: AssignmentService loads candidates (staff ids ordered by staff
record age) and StaffRepository.count_open_workloads().
"""

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence

from helpdesk.models.exceptions import DomainError


class AssignmentStrategy(ABC):
    """Strategy: AbstractStrategy."""

    @abstractmethod
    def select(
        self, candidates: Sequence[int], open_workloads: Mapping[int, int]
    ) -> int:
        """Pick one staff id. Ties -> first candidate in the given order."""


class FewestOpenTicketsStrategy(AssignmentStrategy):
    """Strategy: ConcreteStrategy - fewest OPEN+IN_PROGRESS tickets wins (BR-8)."""

    def select(
        self, candidates: Sequence[int], open_workloads: Mapping[int, int]
    ) -> int:
        if not candidates:
            raise DomainError("No staff candidates are available for assignment.")
        return min(candidates, key=lambda staff_id: open_workloads.get(staff_id, 0))

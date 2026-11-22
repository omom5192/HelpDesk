"""Staff assignment policies.

AssignmentService asks the selected strategy which staff member to use.
"""

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence

from helpdesk.models.exceptions import DomainError


class AssignmentStrategy(ABC):
    """Common interface for assignment policies."""

    @abstractmethod
    def select(
        self, candidates: Sequence[int], open_workloads: Mapping[int, int]
    ) -> int:
        """Pick one staff id. Ties -> first candidate in the given order."""


class FewestOpenTicketsStrategy(AssignmentStrategy):
    """Picks the staff member with the fewest open tickets (BR-8)."""

    def select(
        self, candidates: Sequence[int], open_workloads: Mapping[int, int]
    ) -> int:
        if not candidates:
            raise DomainError("No staff candidates are available for assignment.")
        return min(candidates, key=lambda staff_id: open_workloads.get(staff_id, 0))

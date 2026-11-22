"""Strategy pattern: ordering (BR-4/BR-5) and assignment (BR-8)."""

from datetime import UTC, datetime, timedelta

import pytest

from helpdesk.models.exceptions import DomainError
from helpdesk.models.ticket import Ticket
from helpdesk.patterns.strategy.assignment_strategies import FewestOpenTicketsStrategy
from helpdesk.patterns.strategy.ordering_strategies import (
    DeadlineOrderingStrategy,
    PriorityOrderingStrategy,
    TicketOrderingStrategy,
)

BASE = datetime(2026, 11, 2, 9, 0, tzinfo=UTC)


def make_ticket(name, priority="MEDIUM", age=0, deadline=None, **extra):
    return Ticket(
        title=f"{name} title",
        description=f"{name} description",
        category="ACCOUNT",
        affected_account="tester",
        priority=priority,
        created_at=BASE - timedelta(days=age),
        deadline=deadline,
        **extra,
    )


def test_priority_strategy_orders_critical_high_medium_low():
    tickets = [
        make_ticket("low", "LOW"),
        make_ticket("critical", "CRITICAL"),
        make_ticket("medium", "MEDIUM"),
        make_ticket("high", "HIGH"),
    ]
    ordered = PriorityOrderingStrategy().order(tickets)
    assert [t.title.split()[0] for t in ordered] == [
        "critical", "high", "medium", "low"
    ]


def test_priority_strategy_breaks_ties_by_oldest_created_first():
    tickets = [
        make_ticket("young", "HIGH", age=1),
        make_ticket("old", "HIGH", age=5),
    ]
    ordered = PriorityOrderingStrategy().order(tickets)
    assert ordered[0].title.startswith("old")


def test_priority_strategy_does_not_mutate_the_input_list():
    tickets = [make_ticket("low", "LOW"), make_ticket("high", "HIGH")]
    original = list(tickets)
    PriorityOrderingStrategy().order(tickets)
    assert tickets == original


def test_deadline_strategy_orders_earliest_deadline_first():
    tickets = [
        make_ticket("late", deadline=BASE + timedelta(days=5)),
        make_ticket("soon", deadline=BASE + timedelta(days=1)),
    ]
    ordered = DeadlineOrderingStrategy().order(tickets)
    assert ordered[0].title.startswith("soon")


def test_deadline_strategy_puts_null_deadlines_last():
    tickets = [
        make_ticket("none"),
        make_ticket("some", deadline=BASE + timedelta(days=3)),
    ]
    ordered = DeadlineOrderingStrategy().order(tickets)
    assert ordered[-1].title.startswith("none")


def test_deadline_strategy_uses_priority_as_a_tiebreaker():
    tickets = [
        make_ticket("low", "LOW", deadline=BASE + timedelta(days=2)),
        make_ticket("high", "HIGH", deadline=BASE + timedelta(days=2)),
    ]
    ordered = DeadlineOrderingStrategy().order(tickets)
    assert ordered[0].title.startswith("high")


def test_deadline_strategy_accepts_naive_datetimes():
    naive = datetime(2026, 11, 3, 9, 0)
    ticket = make_ticket("naive", deadline=naive)
    assert DeadlineOrderingStrategy().order([ticket]) == [ticket]


def test_both_strategies_share_one_interface():
    for strategy in (PriorityOrderingStrategy(), DeadlineOrderingStrategy()):
        assert isinstance(strategy, TicketOrderingStrategy)


def test_unknown_priority_is_rejected_by_the_strategy():
    ticket = make_ticket("weird")
    ticket.priority = "PURPLE"
    with pytest.raises(ValueError, match="Unknown priority"):
        PriorityOrderingStrategy().order([ticket])


def test_service_can_hot_swap_its_ordering_strategy(service):
    early = service.create_ticket(
        title="No deadline ticket", description="This ticket has no deadline at all",
        category="TECHNICAL", priority="LOW", component="network",
    )
    soon = service.create_ticket(
        title="Soon deadline ticket", description="This ticket has a near deadline",
        category="TECHNICAL", priority="HIGH", component="network",
        deadline=datetime(2026, 11, 3, 9, 0, tzinfo=UTC),
    )
    assert service.list_tickets()[0].id == soon.id  # default: priority

    service.set_ordering_strategy(DeadlineOrderingStrategy())
    assert service.list_tickets()[0].id == soon.id
    assert service.list_tickets()[-1].id == early.id


def test_assignment_strategy_picks_the_least_loaded_candidate():
    strategy = FewestOpenTicketsStrategy()
    assert strategy.select([1, 2, 3], {1: 5, 2: 1, 3: 3}) == 2


def test_assignment_strategy_ties_go_to_the_first_candidate():
    strategy = FewestOpenTicketsStrategy()
    assert strategy.select([4, 5, 6], {4: 2, 5: 2, 6: 2}) == 4


def test_assignment_strategy_treats_missing_workloads_as_zero():
    assert FewestOpenTicketsStrategy().select([9, 10], {9: 3}) == 10


def test_assignment_strategy_with_no_candidates_is_a_domain_error():
    with pytest.raises(DomainError, match="No staff candidates"):
        FewestOpenTicketsStrategy().select([], {})


def test_assignment_service_auto_uses_the_strategy(assignment, service, staff_repository):
    for name in ("A", "B"):
        staff_repository.add(f"Staff {name}")
    ticket = service.create_ticket(
        title="Assign me please", description="A ticket that needs auto assignment",
        category="TECHNICAL", priority="HIGH", component="network",
    )
    chosen = assignment.assign(ticket.id)
    assert chosen.assigned_staff_id == 1  # both zero -> first by staff id

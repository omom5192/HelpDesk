# Integration coverage

## What counts as integration here

A unit test pins one class in isolation. An integration test crosses at least
**two** of these boundaries:

1. CLI -> Service
2. Service -> Factory / Strategy / State
3. Service -> Repository -> SQLite
4. Publisher -> Observer -> Decorator -> notification channel / activity table

## Coverage matrix

| Scenario | Patterns crossed | File |
| --- | --- | --- |
| Create -> DB round-trip -> TicketCreated -> activity row | Factory, Observer | `test_integration.py::test_create_ticket_notifies_and_logs_the_activity` |
| Decorator stack emits LOG + URGENT | Observer, Decorator | `test_integration.py::test_decorator_stack_logs_and_prefixes_urgent_notifications` |
| Full lifecycle OPEN->IN_PROGRESS->RESOLVED->CLOSED->REOPEN | State, Repository, Observer | `test_integration.py::test_full_lifecycle_publishes_every_status_change` |
| Three categories created through registry | Factory, Repository | `test_integration.py::test_all_three_categories_create_through_the_registry` |
| BR-7 rejection after resolution | State, Assignment | `test_integration.py::test_assignment_is_refused_for_resolved_tickets` |
| BR-8 AUTO assignment after seeding workloads | Strategy, Repository, Assignment | `test_integration.py::test_auto_assignment_prefers_the_least_loaded_staff` |
| Runtime ordering switch | Strategy, Service, CLI (option 4) | `test_integration.py::test_ordering_strategy_switch_changes_service_output` |
| Composition root builds the whole graph | all | `test_integration.py::test_composition_root_builds_a_usable_menu_object` |
| Seeded demo: two AUTO picks -> staff 5, 6 | Seed, Strategy, Repository | `test_integration_suite.py::test_seeded_auto_assignment_uses_the_two_free_staff` |
| Seeded BR-2 demo | Seed, State, Service | `test_integration_suite.py::test_seeded_reopen_window_is_demo_ready` |
| Observer failure isolation | Observer, Service | `test_integration_suite.py::test_observer_failure_does_not_break_the_use_case` |
| Event immutability through decorator stack | Observer, Decorator | `test_integration_suite.py::test_event_messages_are_immutable_across_decorators` |
| CLI code parsing + menu loop, literal `AUTO` and invalid staff input | CLI -> AssignmentService | `tests/test_cli_parsing.py` |

## Single-pattern evidence (for completeness)

| Pattern | Dedicated file |
| --- | --- |
| State | `tests/test_state.py`, `tests/test_state_matrix.py`, `tests/test_reopen_window.py` |
| Factory Method | `tests/test_factory.py` |
| Strategy | `tests/test_strategy.py` |
| Observer | `tests/test_observer.py`, `tests/test_ticket_service.py` |
| Decorator | `tests/test_decorator.py` |

## G-series demo checklist

| Demo | Steps | Expected |
| --- | --- | --- |
| G1 create all categories | CLI 1 x3 | three tickets with category-specific fields |
| G2 ordering switch | CLI 4 then 2 | priority vs deadline order differs |
| G3 AUTO assignment | CLI 5 twice on fresh DB | staff 5, then staff 6 |
| G4 illegal transition | CLI 7: close an IN_PROGRESS ticket | `Rejected: Cannot close: ... must be resolved first` |
| G5 reopen windows | CLI 7: reopen both seeded CLOSED tickets | recent succeeds, old is refused with "7 days" |
| G6 observer/decorator output | create a CRITICAL ticket | `[LOG]` and `[URGENT]` lines + activity row |

# README contribution - M2 (patterns)

## README additions

- Description now lists all five patterns: Factory Method, State, Strategy,
  Observer, Decorator.
- Menu now documents options 1-7, including runtime strategy switching (4),
  assignment (5), workload view (6) and lifecycle transitions (7).
- The layout notes identify `models/ticket.py` as the State Context and the
  Factory Method Product base.
- Design notes explain that the BR-1 matrix lives only in
  `patterns/state/states.py`, and that the seed keeps the BR-2 window usable.

## M2 implementation surface

- **State:** `Ticket` delegates `start_progress/resolve/close/reopen` to one
  of four stateless singleton states; BR-1 matrix + BR-2 window centralised;
  `tests/test_state.py`, `test_state_matrix.py`, `test_reopen_window.py`.
- **Factory Method:** one creator per category, registry lookup in
  `TicketService`, three concrete products with category behaviour;
  `tests/test_factory.py`.
- **Strategy:** priority/deadline ordering with runtime switch, plus
  fewest-open-tickets assignment; `tests/test_strategy.py`,
  `AssignmentService`, `StaffRepository.count_open_workloads`.
- Product state/category fields are persisted through the existing single
  `tickets` table - no schema migration was needed.

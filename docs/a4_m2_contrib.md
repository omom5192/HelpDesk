# A4 individual contribution - M2 (State / Factory Method / Strategy)

## What I implemented

1. **State pattern** (`patterns/state/`, `models/ticket.py`)
   - Context `Ticket` delegates all lifecycle operations to the current state.
   - Four stateless singleton states own the complete BR-1 matrix; BR-2 reopen
     window is inclusive at 7 days, with a clear reason for every rejection.
   - Reopen clears `closed_at` and the stale resolution note.

2. **Factory Method** (`patterns/factory/`)
   - `TicketCreator` + three concrete creators; `CREATOR_REGISTRY` is the only
     public lookup point. Category-specific mandatory fields and default
     priorities are enforced at creation time.
   - Three products (`TechnicalTicket`, `AccountTicket`, `HardwareTicket`)
     share the base Ticket but add behavior (`escalation_level`, `is_lockout`
     with word boundaries, `is_warranty_eligible`).

3. **Strategy pattern** (`patterns/strategy/`, services)
   - `PriorityOrderingStrategy` (BR-4), `DeadlineOrderingStrategy` (BR-5,
     null deadlines last), both pure (input list untouched).
   - `FewestOpenTicketsStrategy` (BR-8) with stable tie-break; contexts
     `TicketService` and `AssignmentService` allow hot swapping.
   - `AssignmentService` enforces BR-7 and publishes `StaffAssignedEvent`.

## Design decisions

- `state_for()` is documented as infrastructure mapping, **not** a Factory
  Method (no creator hierarchy).
- States import `Ticket` only under `TYPE_CHECKING` to avoid an import cycle.
- `Ticket.status` stays an alias of `status_code` for compatibility;
  `status_display` exposes the human-readable name.

## Evidence

`tests/test_state.py`, `test_state_matrix.py`, `test_reopen_window.py`,
`test_factory.py`, `test_strategy.py`, `tests/test_integration.py`.

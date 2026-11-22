# State pattern - lifecycle state machine (BR-1 / BR-2)

## State diagram

```mermaid
stateDiagram-v2
    [*] --> OPEN : create
    OPEN --> IN_PROGRESS : start_progress
    OPEN --> RESOLVED : resolve(note >= 3)
    OPEN --> CLOSED : close (duplicate)
    IN_PROGRESS --> RESOLVED : resolve(note >= 3)
    RESOLVED --> CLOSED : close
    RESOLVED --> IN_PROGRESS : reopen (not fixed)
    CLOSED --> IN_PROGRESS : reopen within 7 days
    CLOSED --> CLOSED : reopen after 7 days -> InvalidTransitionError
```

Every arrow not drawn is an **explicit rejection** implemented in the source
state (never a silent no-op). `tests/test_state_matrix.py` pins all 16 cells.

## Class structure

```mermaid
classDiagram
    class Ticket {
        -state: TicketState
        +start_progress()
        +resolve(note)
        +close(note)
        +reopen()
        +status_code: str
        +_transition_to(next)
    }
    class TicketState {
        <<abstract>>
        +start_progress(ticket)*
        +resolve(ticket, note)*
        +close(ticket, note)*
        +reopen(ticket)*
        #_close_now(ticket)
        #_reopen_to_progress(ticket)
    }
    class OpenState
    class InProgressState
    class ResolvedState
    class ClosedState

    Ticket o-- TicketState : Context (one current state)
    TicketState <|-- OpenState
    TicketState <|-- InProgressState
    TicketState <|-- ResolvedState
    TicketState <|-- ClosedState
```

## Reopen decision (BR-2)

```
reopen() on CLOSED:
    closed_at is None          -> InvalidTransitionError("without a timestamp")
    now - closed_at > 7 days   -> InvalidTransitionError("more than 7 days ago")
    otherwise                  -> closed_at = None; resolution_note = None;
                                  state = IN_PROGRESS
```

The boundary is inclusive; a millisecond of scheduling jitter is tolerated,
one second past the boundary is refused. Code:
`src/helpdesk/patterns/state/states.py`. Evidence: `tests/test_state.py`,
`tests/test_state_matrix.py`, `tests/test_reopen_window.py`.

# Strategy pattern - ordering and assignment

Two independent Strategy families share the same shape: a Context holds one
policy object and calls it through an abstract interface.

```mermaid
classDiagram
    class TicketOrderingStrategy {
        <<abstract>>
        +order(tickets)* List~Ticket~
    }
    class PriorityOrderingStrategy {
        +order(tickets) List~Ticket~
    }
    class DeadlineOrderingStrategy {
        +order(tickets) List~Ticket~
    }
    class TicketService {
        -ordering: TicketOrderingStrategy
        +set_ordering_strategy(strategy)
        +list_tickets() List~Ticket~
    }
    class AssignmentStrategy {
        <<abstract>>
        +select(candidates, workloads)* int
    }
    class FewestOpenTicketsStrategy {
        +select(candidates, workloads) int
    }
    class AssignmentService {
        -strategy: AssignmentStrategy
        +set_assignment_strategy(strategy)
        +assign(ticket_id, staff_id) Ticket
    }

    TicketOrderingStrategy <|-- PriorityOrderingStrategy
    TicketOrderingStrategy <|-- DeadlineOrderingStrategy
    TicketService o-- TicketOrderingStrategy : Context holds ONE
    AssignmentStrategy <|-- FewestOpenTicketsStrategy
    AssignmentService o-- AssignmentStrategy : Context holds ONE
```

## Sequence: switching ordering at runtime (FR-10)

```mermaid
sequenceDiagram
    actor User
    participant CLI as ConsoleMenu
    participant S as TicketService
    participant P as PriorityOrderingStrategy
    participant D as DeadlineOrderingStrategy
    User->>CLI: choose [4] then [2]
    CLI->>S: set_ordering_strategy(DeadlineOrderingStrategy())
    User->>CLI: choose [2] List
    CLI->>S: list_tickets()
    S->>D: order(tickets)
    D-->>S: sorted copy (input untouched)
    S-->>CLI: ordered tickets
```

**Contexts:** `TicketService` (ordering) and `AssignmentService` (assignment).
**Evidence:** `tests/test_strategy.py`, `tests/test_integration.py`.

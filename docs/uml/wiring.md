# Wiring diagram - full object graph

The composition root is the only place that names concrete classes and builds
the object graph (`src/helpdesk/main.py::build_application`).

```mermaid
flowchart TB
    CLI[ConsoleMenu] -->|use cases| TS[TicketService]
    CLI -->|use cases| AS[AssignmentService]
    TS -->|save/find| TR[TicketRepository]
    AS -->|save/get| TR
    AS -->|list/count| SR[StaffRepository]
    TS -->|publish| PUB[TicketEventPublisher]
    AS -->|publish| PUB
    PUB -->|notify| DEC[Logging(Urgent(Console))]
    PUB -->|notify| ALO[ActivityLogObserver]
    DEC --> CON[ConsoleNotificationObserver]
    ALO --> AR[ActivityRepository]
    TR --> DB[(Database / SQLite)]
    SR --> DB
    AR --> DB
    TS -.->|holds| ORD[Ordering Strategy]
    AS -.->|holds| ASS[Assignment Strategy]
    TS -.->|resolves category| REG[CREATOR_REGISTRY]
    REG -.-> CRE[Concrete Creators]
```

## Sequence: application startup

```mermaid
sequenceDiagram
    participant M as main.build_application
    participant DB as Database
    participant P as TicketEventPublisher
    participant S as TicketService
    participant A as AssignmentService
    participant C as ConsoleMenu
    M->>DB: initialize()
    M->>P: subscribe(Logging(Urgent(Console)))
    M->>P: subscribe(ActivityLogObserver)
    M->>S: new TicketService(tickets, staff, P)
    M->>A: new AssignmentService(DB, P)
    M->>C: new ConsoleMenu(S, A)
    C-->>M: ready to run()
```

## Sequence: create -> assign -> resolve

```mermaid
sequenceDiagram
    actor U
    participant C as ConsoleMenu
    participant S as TicketService
    participant F as CREATOR_REGISTRY
    participant R as TicketRepository
    participant P as Publisher
    participant A as AssignmentService
    participant W as StaffRepository
    U->>C: [1] create TECHNICAL
    C->>S: create_ticket(...)
    S->>F: creator for category
    F-->>S: TechnicalTicket
    S->>R: save
    S->>P: TicketCreated
    U->>C: [5] assign AUTO
    C->>A: assign(id)
    A->>W: count_open_workloads()
    A->>R: save(assigned)
    A->>P: StaffAssignedEvent
    U->>C: [7] resolve
    C->>S: transition(id, RESOLVED, note)
    S->>R: save(new state)
    S->>P: TicketStatusChanged
```

Evidence: `tests/test_integration.py`, `tests/test_integration_suite.py`,
`tests/test_cli_parsing.py`.

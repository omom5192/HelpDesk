# Factory Method pattern - ticket categories

```mermaid
classDiagram
    class TicketCreator {
        <<abstract>>
        +category: str
        +default_priority: str
        +create(title, description, deadline, created_at, **fields)* Ticket
        #_require(field, value, rule) str
        #_apply_default_priority(priority) str
    }
    class TechnicalTicketCreator {
        +category = TECHNICAL
        +create(...) Ticket
        -_component(value) str
    }
    class AccountTicketCreator {
        +category = ACCOUNT
        +create(...) Ticket
        -_affected_account(value) str
    }
    class HardwareTicketCreator {
        +category = HARDWARE
        +create(...) Ticket
        -_asset_tag(value) str
        -_location(value) str
    }
    class Ticket {
        +id, title, description, category, priority
        +created_at, deadline, closed_at, resolution_note
        +state: TicketState
    }
    class TechnicalTicket {
        +component
        +escalation_level()
    }
    class AccountTicket {
        +is_lockout()
    }
    class HardwareTicket {
        +is_warranty_eligible()
    }
    class CREATOR_REGISTRY {
        <<module dict>>
        TECHNICAL -> TechnicalTicketCreator
        ACCOUNT -> AccountTicketCreator
        HARDWARE -> HardwareTicketCreator
    }
    class TicketService {
        +create_ticket(category, ...)
    }

    TicketCreator <|-- TechnicalTicketCreator
    TicketCreator <|-- AccountTicketCreator
    TicketCreator <|-- HardwareTicketCreator
    Ticket <|-- TechnicalTicket
    Ticket <|-- AccountTicket
    Ticket <|-- HardwareTicket
    TechnicalTicketCreator ..> TechnicalTicket : creates
    AccountTicketCreator ..> AccountTicket : creates
    HardwareTicketCreator ..> HardwareTicket : creates
    CREATOR_REGISTRY o-- TicketCreator
    TicketService --> CREATOR_REGISTRY : resolves category
```

## Sequence: create through the factory

```mermaid
sequenceDiagram
    actor User
    participant CLI
    participant S as TicketService
    participant R as CREATOR_REGISTRY
    participant C as TechnicalTicketCreator
    participant Repo as TicketRepository
    User->>CLI: create TECHNICAL ticket
    CLI->>S: create_ticket(category=TECHNICAL, component=email, ...)
    S->>R: get("TECHNICAL")
    R-->>S: TechnicalTicketCreator
    S->>C: create(now=service clock, fields...)
    C->>C: require/validate component, title, priority
    C-->>S: TechnicalTicket (Product)
    S->>Repo: save(ticket)
    S->>S: publish TicketCreated
```

The clock is owned by the service (contract amendment #1); creators only
validate and build. Evidence: `tests/test_factory.py` (18+ tests).

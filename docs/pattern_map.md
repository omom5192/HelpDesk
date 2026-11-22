# Pattern map

This is the authoritative map from each GoF pattern to its roles in this
repository. A class appears in a pattern role **only** where listed here.

| Pattern | Role | Code |
| --- | --- | --- |
| **Factory Method** | Creator (abstract) | `patterns/factory/abstract_creator.py::TicketCreator` |
| | Concrete Creators | `technical_creator.py`, `account_creator.py`, `hardware_creator.py` |
| | Product (abstract) | `models/ticket.py::Ticket` |
| | Concrete Products | `TechnicalTicket`, `AccountTicket`, `HardwareTicket` |
| | Registry (wiring) | `patterns/factory/__init__.py::CREATOR_REGISTRY` |
| **State** | Context | `models/ticket.py::Ticket` (holds `state`, delegates lifecycle calls) |
| | Abstract State | `patterns/state/base_state.py::TicketState` |
| | Concrete States | `patterns/state/states.py::OpenState`, `InProgressState`, `ResolvedState`, `ClosedState` |
| | Singletons | `OPEN_STATE`, `IN_PROGRESS_STATE`, `RESOLVED_STATE`, `CLOSED_STATE` |
| **Strategy** | Abstract Strategy (ordering) | `patterns/strategy/ordering_strategies.py::TicketOrderingStrategy` |
| | Concrete Strategies | `PriorityOrderingStrategy` (BR-4), `DeadlineOrderingStrategy` (BR-5) |
| | Context | `services/ticket_service.py::TicketService` |
| | Abstract Strategy (assignment) | `patterns/strategy/assignment_strategies.py::AssignmentStrategy` |
| | Concrete Strategy | `FewestOpenTicketsStrategy` (BR-8) |
| | Context | `services/assignment_service.py::AssignmentService` |
| **Observer** | Subject | `patterns/observer/publisher.py::TicketEventPublisher` |
| | Observer interface | `patterns/observer/observers.py::TicketObserver` |
| | Concrete Observers | `ConsoleNotificationObserver`, `ActivityLogObserver` |
| | Events | `patterns/observer/events.py` (`TicketCreated`, `TicketStatusChanged`, `StaffAssignedEvent`) |
| **Decorator** | Component | `TicketObserver` (same interface - Decorator extends an existing Observer) |
| | Concrete Component | `ConsoleNotificationObserver` (default-in-init console channel) |
| | Base Decorator | `patterns/decorator/notification_decorators.py::NotificationDecorator` |
| | Concrete Decorators | `LoggingNotificationDecorator`, `UrgentNotificationDecorator` |
| | Composition root | `main.py::build_application` builds `Logging(Urgent(Console))` |

## Explicit non-patterns

These look similar to patterns but are deliberately **not** claimed as such:

- `state_for()` in `states.py` is an infrastructure lookup (a dict mapping),
  not a Factory Method: it has no creator hierarchy and no product
  polymorphism.
- `ConsoleNotificationService` is a notification channel (a service
  interface), not a Decorator.
- `TicketRepository` is a Data Mapper-style repository, not a GoF pattern.

## Dependency direction

```
cli  ->  services  ->  patterns/*  ->  models  ->  database
                  \->  repositories ------------>  database
```

The domain model never imports services, repositories or the CLI. State
classes refer to `Ticket` only under `TYPE_CHECKING`, which breaks the
`Ticket <-> State` import cycle.

## Requirement coverage (quick index)

| Req | Mechanism |
| --- | --- |
| BR-1 lifecycle | State matrix in `patterns/state/states.py`, audited by `tests/test_state_matrix.py` |
| BR-2 reopen window | `ClosedState.reopen`, audited by `tests/test_reopen_window.py` |
| BR-3 resolution note | `validate_resolution_note`, used by `OpenState.resolve` / `InProgressState.resolve` |
| BR-4 priority ordering | `PriorityOrderingStrategy` |
| BR-5 deadline ordering | `DeadlineOrderingStrategy` |
| BR-6 category fields | Factory Creators, audited by `tests/test_factory.py` |
| BR-7 assignment eligibility | `AssignmentService.assign` |
| BR-8 least-loaded assignment | `FewestOpenTicketsStrategy` + `StaffRepository.count_open_workloads` |
| BR-9 tokens | `models/ticket_types.py` + validators |
| FR-10 runtime strategy switch | `TicketService.set_ordering_strategy`, CLI option 4 |

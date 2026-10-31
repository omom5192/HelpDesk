# Decorator pattern - notification stack

Composition root (`main.py`) builds `Logging(Urgent(Console))`.

```mermaid
classDiagram
    class TicketObserver {
        <<abstract>>
        +update(event)*
    }
    class NotificationObserver {
        -notifications: NotificationService
        +update(event)
    }
    class ConsoleNotificationObserver {
        +update(event)
    }
    class NotificationDecorator {
        -wrapped: TicketObserver
        +update(event)
    }
    class LoggingNotificationDecorator {
        +log_entries: List~str~
        +update(event)
    }
    class UrgentNotificationDecorator {
        +update(event)
    }
    class TicketEventPublisher {
        -observers: List~TicketObserver~
        +subscribe(observer)
        +unsubscribe(observer)
        +publish(event)
    }

    TicketObserver <|-- NotificationObserver
    NotificationObserver <|-- ConsoleNotificationObserver
    TicketObserver <|-- NotificationDecorator
    NotificationDecorator <|-- LoggingNotificationDecorator
    NotificationDecorator <|-- UrgentNotificationDecorator
    NotificationDecorator o-- TicketObserver : wraps ONE component
    TicketEventPublisher o-- TicketObserver : notifies MANY (Observer)
```

| Role | Class |
|---|---|
| Component | `TicketObserver` (reused from Observer, W1) |
| ConcreteComponent | `ConsoleNotificationObserver` |
| BaseDecorator | `NotificationDecorator` |
| ConcreteDecorators | `LoggingNotificationDecorator`, `UrgentNotificationDecorator` |

Code: `src/helpdesk/patterns/decorator/notification_decorators.py` · Evidence: `tests/test_decorator.py` (8 tests)

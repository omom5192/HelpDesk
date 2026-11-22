"""Observer: interface + ConcreteObservers."""

from abc import ABC, abstractmethod

from helpdesk.patterns.decorator.notification import (
    ConsoleNotificationService,
    NotificationService,
)
from helpdesk.patterns.observer.events import TicketEvent


class TicketObserver(ABC):
    """Observer: interface. Also the Decorator pattern's Component."""

    @abstractmethod
    def update(self, event: TicketEvent) -> None: ...


class NotificationObserver(TicketObserver):
    """Observer: ConcreteObserver - dispatches through the notification pipeline."""

    def __init__(self, notifications: NotificationService) -> None:
        self._notifications = notifications

    def update(self, event: TicketEvent) -> None:
        self._notifications.send(
            "console", f"[#{event.ticket_id}] {event.message}"
        )


class ConsoleNotificationObserver(NotificationObserver):
    """NotificationObserver with a console service as default-in-init.

    This is the Decorator pattern's ConcreteComponent; the composition
    root is the only place that stacks decorators around it.
    """

    def __init__(self, notifications: NotificationService | None = None) -> None:
        super().__init__(notifications or ConsoleNotificationService())


class ActivityLogObserver(TicketObserver):
    """Observer: ConcreteObserver - appends ticket_activity rows."""

    def __init__(self, activity) -> None:
        self._activity = activity

    def update(self, event: TicketEvent) -> None:
        self._activity.append(
            event.ticket_id, event.name, event.description, event.occurred_at
        )

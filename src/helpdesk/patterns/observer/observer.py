"""Observer interface and concrete ticket event observers."""

from abc import ABC, abstractmethod

from helpdesk.patterns.decorator.notification import NotificationService
from helpdesk.patterns.observer.events import TicketEvent


class TicketObserver(ABC):
    """Interface that all ticket event observers implement."""

    @abstractmethod
    def update(self, event: TicketEvent) -> None:
        """Handle a ticket event."""
        ...


class NotificationObserver(TicketObserver):
    """Send a ticket event through the notification service."""

    def __init__(self, notifications: NotificationService) -> None:
        self._notifications = notifications

    def update(self, event: TicketEvent) -> None:
        self._notifications.send(
            "console",
            f"[#{event.ticket_id}] {event.description}",
        )


class ActivityLogObserver(TicketObserver):
    """Append a ticket event to the activity log."""

    def __init__(self, activity) -> None:
        self._activity = activity

    def update(self, event: TicketEvent) -> None:
        self._activity.append(
            event.ticket_id,
            event.name,
            event.description,
            event.occurred_at,
        )

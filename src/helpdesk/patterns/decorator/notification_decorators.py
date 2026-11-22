"""Optional extras for notifications.

These wrap a TicketObserver, so main.py can stack them however it likes
without touching the observers themselves. Logging is outermost so it
sees urgent messages too.
"""

from dataclasses import replace
from datetime import datetime, timezone
from typing import Any

from helpdesk.patterns.observer.observer import TicketObserver

_URGENT_PRIORITIES = frozenset({"HIGH", "CRITICAL"})


def _priority_of(event: Any) -> str:
    """Priority whether the event holds it directly or via its ticket."""
    priority = getattr(event, "priority", None)
    if priority is None and getattr(event, "ticket", None) is not None:
        priority = getattr(event.ticket, "priority", None)
    return (priority or "").upper()


class NotificationDecorator(TicketObserver):
    """Pass everything through to the wrapped observer."""

    def __init__(self, wrapped: TicketObserver) -> None:
        self._wrapped = wrapped

    def update(self, event: Any) -> None:
        self._wrapped.update(event)


class LoggingNotificationDecorator(NotificationDecorator):
    """Keeps a log of every notification that comes through."""

    def __init__(self, wrapped: TicketObserver) -> None:
        super().__init__(wrapped)
        self.log_entries: list[str] = []

    def update(self, event: Any) -> None:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        entry = f"{stamp} {type(event).__name__}: {getattr(event, 'message', '')}"
        self.log_entries.append(entry)
        print(f"[LOG] {entry}")
        super().update(event)


class UrgentNotificationDecorator(NotificationDecorator):
    """Mark HIGH/CRITICAL notifications as urgent.

    Events stay immutable: we forward a shallow copy with the message
    prefixed (dataclasses.replace). The original event is untouched - the
    publisher may hand the SAME event to many observers, so mutation would
    leak from one observer to another.
    """

    def update(self, event: Any) -> None:
        if _priority_of(event) in _URGENT_PRIORITIES:
            event = replace(event, message=f"[URGENT] {event.message}")
        super().update(event)

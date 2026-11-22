"""Backward-compatible import path for the Observer classes.

The implementation lives in ``helpdesk.patterns.observer.observers``.
"""

from helpdesk.patterns.observer.observers import (
    ActivityLogObserver,
    ConsoleNotificationObserver,
    NotificationObserver,
    TicketObserver,
)

__all__ = [
    "TicketObserver",
    "NotificationObserver",
    "ConsoleNotificationObserver",
    "ActivityLogObserver",
]

"""Notification channel: service interface and the console implementation.

The Decorator pattern itself lives in notification_decorators.py and wraps
observers (TicketObserver), not these services.
"""

from abc import ABC, abstractmethod


class NotificationService(ABC):
    """Interface for a channel that delivers notification messages."""

    @abstractmethod
    def send(self, recipient: str, message: str) -> None:
        ...


class ConsoleNotificationService(NotificationService):
    """Channel that prints notifications to the console."""

    def send(self, recipient: str, message: str) -> None:
        print(f"[{recipient}] {message}")

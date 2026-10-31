"""Notification pipeline: component, console service, and decorator base."""

from abc import ABC, abstractmethod


class NotificationService(ABC):
    """Component interface for sending notifications."""

    @abstractmethod
    def send(self, recipient: str, message: str) -> None:
        ...


class ConsoleNotificationService(NotificationService):
    """Concrete component that prints notifications to the console."""

    def send(self, recipient: str, message: str) -> None:
        print(f"[{recipient}] {message}")


class NotificationDecorator(NotificationService):
    """Base decorator that wraps another notification service.

    By default it forwards to the wrapped service; concrete decorators
    override ``send`` and call ``super().send(...)`` to keep the chain going.
    """

    def __init__(self, wrapped: NotificationService) -> None:
        self._wrapped = wrapped

    def send(self, recipient: str, message: str) -> None:
        self._wrapped.send(recipient, message)

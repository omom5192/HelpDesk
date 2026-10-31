"""Decorator tests: notification stack (M3 - W2)."""

from dataclasses import dataclass

from helpdesk.patterns.decorator.notification_decorators import (
    LoggingNotificationDecorator,
    NotificationDecorator,
    UrgentNotificationDecorator,
)
from helpdesk.patterns.observer.observer import (
    ConsoleNotificationObserver,
    TicketObserver,
)


@dataclass
class FakeEvent:
    message: str = "New ticket HD-1: printer on fire"
    priority: str = "MEDIUM"


class RecordingObserver(TicketObserver):
    """Local stand-in - deliberately NOT in conftest (that file is M1's)."""

    def __init__(self):
        self.received: list = []

    def update(self, event):
        self.received.append(event)


def test_base_decorator_forwards_unchanged():
    inner = RecordingObserver()
    event = FakeEvent()
    NotificationDecorator(inner).update(event)
    assert inner.received == [event]


def test_logging_records_and_forwards_every_event():
    inner = RecordingObserver()
    outer = LoggingNotificationDecorator(inner)
    outer.update(FakeEvent())
    outer.update(FakeEvent(message="New ticket HD-2"))
    assert len(outer.log_entries) == 2
    assert len(inner.received) == 2


def test_logging_prints_before_forwarding(capsys):
    LoggingNotificationDecorator(RecordingObserver()).update(FakeEvent())
    out = capsys.readouterr().out
    assert "[LOG]" in out and "printer on fire" in out


def test_urgent_prefix_for_critical():
    inner = RecordingObserver()
    UrgentNotificationDecorator(inner).update(FakeEvent(priority="CRITICAL"))
    assert inner.received[0].message.startswith("[URGENT] ")


def test_urgent_prefix_for_high():
    inner = RecordingObserver()
    UrgentNotificationDecorator(inner).update(FakeEvent(priority="HIGH"))
    assert inner.received[0].message.startswith("[URGENT] ")


def test_no_prefix_for_medium_or_low():
    inner = RecordingObserver()
    urgent = UrgentNotificationDecorator(inner)
    urgent.update(FakeEvent(priority="MEDIUM"))
    urgent.update(FakeEvent(priority="LOW"))
    assert not any(e.message.startswith("[URGENT]") for e in inner.received)


def test_original_event_is_never_mutated():
    inner = RecordingObserver()
    event = FakeEvent(priority="HIGH", message="X32 projector dead")
    UrgentNotificationDecorator(inner).update(event)
    assert event.message == "X32 projector dead"  # input untouched
    assert inner.received[0].message.startswith("[URGENT]")


def test_stack_wraps_one_console_instance():
    console = ConsoleNotificationObserver()
    stack = LoggingNotificationDecorator(UrgentNotificationDecorator(console))
    assert isinstance(stack._wrapped, UrgentNotificationDecorator)
    assert stack._wrapped._wrapped is console  # composition, not copies

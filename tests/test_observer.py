"""Observer tests: subscription, notification, and failure isolation."""

from datetime import datetime, timezone

from helpdesk.patterns.observer.events import TicketCreated
from helpdesk.patterns.observer.publisher import TicketEventPublisher


class RecordingObserver:
    def __init__(self):
        self.received = []

    def update(self, event):
        self.received.append(event)


class FailingObserver:
    def update(self, event):
        raise RuntimeError("observer failed")


def make_event():
    return TicketCreated(
        ticket_id=1,
        occurred_at=datetime.now(timezone.utc),
        title="Printer issue",
        category="HARDWARE",
        priority="MEDIUM",
    )


def test_subscribe_and_publish_notifies_observer():
    publisher = TicketEventPublisher()
    observer = RecordingObserver()
    event = make_event()

    publisher.subscribe(observer)
    publisher.publish(event)

    assert observer.received == [event]


def test_subscribe_does_not_add_same_observer_twice():
    publisher = TicketEventPublisher()
    observer = RecordingObserver()
    event = make_event()

    publisher.subscribe(observer)
    publisher.subscribe(observer)
    publisher.publish(event)

    assert observer.received == [event]


def test_unsubscribe_stops_notifications():
    publisher = TicketEventPublisher()
    observer = RecordingObserver()

    publisher.subscribe(observer)
    publisher.unsubscribe(observer)
    publisher.publish(make_event())

    assert observer.received == []


def test_failing_observer_does_not_block_others(caplog):
    publisher = TicketEventPublisher()
    recording_observer = RecordingObserver()
    event = make_event()

    publisher.subscribe(FailingObserver())
    publisher.subscribe(recording_observer)
    publisher.publish(event)

    assert recording_observer.received == [event]
    assert "Observer failed; skipping" in caplog.text
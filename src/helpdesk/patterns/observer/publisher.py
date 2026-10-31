"""Observer subject that publishes ticket events to subscribed observers."""

import logging

from helpdesk.patterns.observer.events import TicketEvent


class TicketEventPublisher:
    """Manage observers and publish events to them."""

    def __init__(self) -> None:
        self._observers = []

    def subscribe(self, observer) -> None:
        """Add an observer unless it is already subscribed."""
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer) -> None:
        """Remove an observer if it is subscribed."""
        if observer in self._observers:
            self._observers.remove(observer)

    def publish(self, event: TicketEvent) -> None:
        """Notify each observer; log failures and continue to the next."""
        for observer in list(self._observers):
            try:
                observer.update(event)
            except Exception:
                logging.getLogger("helpdesk.events").exception(
                    "Observer failed; skipping: %r",
                    observer,
                )
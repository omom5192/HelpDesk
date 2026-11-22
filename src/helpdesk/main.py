"""Application entry point and dependency composition root.

This is the ONLY module that names concrete classes (apart from
default-in-init), which keeps the rest of the code Open/Closed.
"""

from helpdesk.cli.menu import ConsoleMenu
from helpdesk.database.database import Database
from helpdesk.patterns.decorator.notification_decorators import (
    LoggingNotificationDecorator,
    UrgentNotificationDecorator,
)
from helpdesk.patterns.observer.observers import (
    ActivityLogObserver,
    ConsoleNotificationObserver,
)
from helpdesk.patterns.observer.publisher import TicketEventPublisher
from helpdesk.repositories.activity_repository import ActivityRepository
from helpdesk.repositories.staff_repository import StaffRepository
from helpdesk.repositories.ticket_repository import TicketRepository
from helpdesk.services.assignment_service import AssignmentService
from helpdesk.services.ticket_service import TicketService


def build_application(db_path: str = "helpdesk.db") -> ConsoleMenu:
    """Build the complete object graph; dependency injection lives here."""
    database = Database(db_path)
    database.initialize()

    ticket_repo = TicketRepository(database)
    staff_repo = StaffRepository(database)
    activity_repo = ActivityRepository(database)

    publisher = TicketEventPublisher()
    # Decorator stack: Logging(Urgent(Console)); Logging is outermost so
    # urgent notifications are logged too.
    publisher.subscribe(
        LoggingNotificationDecorator(
            UrgentNotificationDecorator(ConsoleNotificationObserver())
        )
    )
    publisher.subscribe(ActivityLogObserver(activity_repo))

    service = TicketService(ticket_repo, staff_repo, publisher)
    assignment = AssignmentService(
        database,
        publisher=publisher,
        ticket_repository=ticket_repo,
        staff_repository=staff_repo,
    )
    return ConsoleMenu(service, assignment)


def main() -> None:
    build_application().run()


if __name__ == "__main__":
    main()

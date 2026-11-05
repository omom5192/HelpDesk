"""Application entry point and dependency composition root."""

from helpdesk.cli.menu import ConsoleMenu
from helpdesk.database.database import Database
from helpdesk.patterns.decorator.notification import ConsoleNotificationService
from helpdesk.patterns.observer.observer import (
    ActivityLogObserver,
    NotificationObserver,
)
from helpdesk.patterns.observer.publisher import TicketEventPublisher
from helpdesk.repositories.activity_repository import ActivityRepository
from helpdesk.repositories.staff_repository import StaffRepository
from helpdesk.repositories.ticket_repository import TicketRepository
from helpdesk.services.ticket_service import TicketService


def build_application(db_path: str = "helpdesk.db") -> ConsoleMenu:
    database = Database(db_path)
    database.initialize()

    ticket_repo = TicketRepository(database)
    staff_repo = StaffRepository(database)
    activity_repo = ActivityRepository(database)

    publisher = TicketEventPublisher()
    publisher.subscribe(NotificationObserver(ConsoleNotificationService()))
    publisher.subscribe(ActivityLogObserver(activity_repo))

    service = TicketService(ticket_repo, staff_repo, publisher)
    return ConsoleMenu(service)


def main() -> None:
    build_application().run()

<<<<<<< HEAD
if __name__ == "__main__" :
   main()
=======

if __name__ == "__main__":
    main()
>>>>>>> d6f5ce911c39ccb1cb20d24fecdc72beb2b8212c

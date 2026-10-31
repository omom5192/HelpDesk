"""Interactive console menu for creating, listing, and viewing tickets."""

from datetime import datetime

from helpdesk.models.exceptions import DomainError
from helpdesk.services.ticket_service import TicketService


class ConsoleMenu:
    def __init__(self, service: TicketService) -> None:
        self._service = service

    def run(self) -> None:
        print("HelpDesk - Ticket Management System")

        while True:
            print("\n[1] Create  [2] List  [3] View  [0] Exit")
            choice = input("> ").strip()

            try:
                if choice == "1":
                    self._handle_create()
                elif choice == "2":
                    self._handle_list()
                elif choice == "3":
                    self._handle_view()
                elif choice == "0":
                    print("Bye.")
                    return
                else:
                    print("Unknown option.")
            except DomainError as exc:
                print(f"Rejected: {exc}")

    def _handle_create(self) -> None:
        title = input("Title: ")
        description = input("Description (min 10 chars): ")

        category = self._ask_choice(
            "Category",
            {"1": "TECHNICAL", "2": "ACCOUNT", "3": "HARDWARE"},
        )
        priority = self._ask_choice(
            "Priority",
            {"1": "LOW", "2": "MEDIUM", "3": "HIGH", "4": "CRITICAL"},
        )
        deadline = self._ask_optional_date(
            "Deadline (YYYY-MM-DD HH:MM, empty = none): "
        )

        ticket = self._service.create_ticket(
            title=title,
            description=description,
            category=category,
            priority=priority,
            deadline=deadline,
        )
        print(f"Created ticket HD-{ticket.id:04d} [{ticket.status_code}]")

    def _handle_list(self) -> None:
        tickets = self._service.list_tickets()

        if not tickets:
            print("No tickets yet.")
            return

        print(f"{'ID':<8} {'STATUS':<12} {'PRIORITY':<9} CATEGORY   TITLE")
        for ticket in tickets:
            print(
                f"HD-{ticket.id:04d}   {ticket.status_code:<12} "
                f"{ticket.priority:<9} {ticket.category:<10} "
                f"{ticket.title[:40]}"
            )

    def _handle_view(self) -> None:
        raw_id = input("Ticket id (HD-0001 or digits): ").strip().upper()
        try:
            ticket_id = int(raw_id.removeprefix("HD-"))
        except ValueError:
            print("Invalid ticket id.")
            return

        ticket = self._service.get_ticket(ticket_id)
        for key, value in ticket.get_details().items():
            print(f"{key}: {value}")

    @staticmethod
    def _ask_choice(label: str, options: dict[str, str]) -> str:
        menu = ", ".join(f"[{key}] {value}" for key, value in options.items())

        while True:
            chosen = input(f"{label} {menu}: ").strip()
            if chosen in options:
                return options[chosen]
            print("Option not recognized.")

    @staticmethod
    def _ask_optional_date(prompt: str) -> datetime | None:
        raw = input(prompt).strip()
        if not raw:
            return None

        while True:
            try:
                return datetime.fromisoformat(raw)
            except ValueError:
                raw = input(
                    "That is not a date. Retry (YYYY-MM-DD HH:MM) or empty: "
                ).strip()
                if not raw:
                    return None
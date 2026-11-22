"""Interactive console menu (create/list/view/order/assign/workloads/transition).

All printing and input live here; the domain and service layers never print.
"""

from datetime import datetime

from helpdesk.models.exceptions import HelpDeskError
from helpdesk.services.assignment_service import AssignmentService
from helpdesk.services.ticket_service import TicketService


def parse_ticket_code(raw: str) -> int | None:
    """'HD-3', ' hd-42 ' -> id. Anything else -> None (caller prints a hint)."""
    code = (raw or "").strip().upper()
    if not code.startswith("HD-"):
        return None
    digits = code[3:]
    return int(digits) if digits.isdigit() else None


def _read_menu_choice() -> str:
    """Read a menu choice; EOF/Ctrl-C exits cleanly instead of crashing."""
    try:
        return input("Choose: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nLeaving HelpDesk.")
        raise SystemExit(0) from None


class ConsoleMenu:
    def __init__(
        self,
        service: TicketService,
        assignment_service: AssignmentService | None = None,
    ) -> None:
        self._service = service
        self._assignment = assignment_service

    def run(self) -> None:
        print("HelpDesk - Ticket Management System")
        while True:
            print(
                "\n[1] Create  [2] List  [3] View  [4] Ordering  "
                "[5] Assign  [6] Workloads  [7] Transition  [0] Exit"
            )
            choice = _read_menu_choice()
            try:
                if choice == "1":
                    self._handle_create()
                elif choice == "2":
                    self._handle_list()
                elif choice == "3":
                    self._handle_view()
                elif choice == "4":
                    self._handle_choose_ordering()
                elif choice == "5":
                    self._handle_assign()
                elif choice == "6":
                    self._handle_workloads()
                elif choice == "7":
                    self._handle_transition()
                elif choice == "0":
                    print("Bye.")
                    return
                else:
                    print("Unknown option.")
            except HelpDeskError as exc:
                print(f"Rejected: {exc}")

    def _handle_create(self) -> None:
        title = input("Title: ")
        description = input("Description (min 10 chars): ")
        category = self._ask_choice(
            "Category", {"1": "TECHNICAL", "2": "ACCOUNT", "3": "HARDWARE"}
        )
        priority = self._ask_choice(
            "Priority",
            {"1": "LOW", "2": "MEDIUM", "3": "HIGH", "4": "CRITICAL"},
        )
        deadline = self._ask_optional_date(
            "Deadline (YYYY-MM-DD HH:MM, empty = none): "
        )

        fields: dict = {}
        if category == "TECHNICAL":
            fields["component"] = input("Component (network/email/...): ").strip()
        elif category == "ACCOUNT":
            fields["affected_account"] = input("Affected account: ").strip()
        else:
            fields["asset_tag"] = input("Asset tag (PC-1234): ").strip()
            fields["location"] = input("Location: ").strip()

        ticket = self._service.create_ticket(
            title=title,
            description=description,
            category=category,
            priority=priority,
            deadline=deadline,
            **fields,
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
                f"{ticket.priority:<9} {ticket.category:<10} {ticket.title[:40]}"
            )

    def _handle_view(self) -> None:
        ticket_id = parse_ticket_code(input("Ticket code (HD-0001 or digits): "))
        if ticket_id is None:
            print("Use the HD-<id> form.")
            return
        for key, value in self._service.get_ticket(ticket_id).get_details().items():
            print(f"{key}: {value}")

    def _handle_choose_ordering(self) -> None:
        from helpdesk.patterns.strategy.ordering_strategies import (
            DeadlineOrderingStrategy,
            PriorityOrderingStrategy,
        )

        print("Ordering strategy:")
        print(" 1. Priority (BR-4: CRITICAL > HIGH > MEDIUM > LOW, oldest first)")
        print(" 2. Deadline (BR-5: earliest first, no-deadline last)")
        choice = input("Select [1/2]: ").strip()
        strategies = {
            "1": (PriorityOrderingStrategy(), "priority ordering active"),
            "2": (DeadlineOrderingStrategy(), "deadline ordering active"),
        }
        entry = strategies.get(choice)
        if entry is None:
            print("Unknown option - ordering strategy unchanged.")
            return
        strategy, label = entry
        self._service.set_ordering_strategy(strategy)
        print(f"OK - {label}.")

    def _handle_assign(self) -> None:
        if self._assignment is None:
            print("Assignment is not configured.")
            return
        ticket_id = parse_ticket_code(input("Ticket code (HD-<id>): "))
        if ticket_id is None:
            print("Use the HD-<id> form - nothing changed.")
            return
        ticket = self._service.get_ticket(ticket_id)
        print(f"HD-{ticket.id:04d}: {ticket.title} [{ticket.status_code}]")
        if ticket.status_code not in ("OPEN", "IN_PROGRESS"):
            print("BR-7: only OPEN or IN_PROGRESS tickets can be assigned.")
            return
        print("Staff (id, name, open workload):")
        for staff_id, name, load in self._assignment.candidate_overview():
            print(f"  {staff_id}. {name} ({load})")
        chosen = input(
            "Press Enter (or type AUTO) for fewest-open assignment, or a staff id: "
        ).strip()
        if chosen.upper() == "AUTO":
            staff_choice = None
        elif not chosen:
            staff_choice = None
        else:
            try:
                staff_choice = int(chosen)
            except ValueError:
                print(f"Not a staff id: {chosen!r} - nothing changed.")
                return
        tail = self._assignment.assign(ticket_id, staff_choice)
        print(f"Assigned HD-{ticket.id:04d} -> staff #{tail.assigned_staff_id}.")

    def _handle_workloads(self) -> None:
        if self._assignment is None:
            print("Assignment is not configured.")
            return
        print("Staff workloads (OPEN + IN_PROGRESS - BR-8):")
        for staff_id, name, load in self._assignment.candidate_overview():
            print(f"  {staff_id:>3}. {name:<20} {load:>2} {'#' * min(load, 10)}")

    def _handle_transition(self) -> None:
        ticket_id = parse_ticket_code(input("Ticket code (HD-<id>): "))
        if ticket_id is None:
            print("Use the HD-<id> form.")
            return
        print("Action: [1] start progress  [2] resolve  [3] close  [4] reopen")
        action = {
            "1": "IN_PROGRESS",
            "2": "RESOLVED",
            "3": "CLOSED",
            "4": "REOPEN",
        }.get(input("Select [1/2/3/4]: ").strip())
        if action is None:
            print("Unknown action - nothing changed.")
            return
        note = input("Resolution note (min 3 chars): ") if action == "RESOLVED" else ""
        ticket = self._service.transition(ticket_id, action, note=note)
        print(f"Ticket HD-{ticket.id:04d} is now {ticket.status_code}.")

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

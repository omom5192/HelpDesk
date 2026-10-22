from helpdesk.models.ticket import Ticket


def test_ticket_starts_open():
    ticket = Ticket(1, "Login problem", "Cannot log in")
    assert ticket.status == "Open"


def test_ticket_status_can_be_updated():
    ticket = Ticket(1, "Login problem", "Cannot log in")
    result = ticket.update_status("In Progress")

    assert result is True
    assert ticket.status == "In Progress"


def test_ticket_rejects_invalid_status():
    ticket = Ticket(1, "Login problem", "Cannot log in")
    result = ticket.update_status("Invalid")

    assert result is False
    assert ticket.status == "Open"

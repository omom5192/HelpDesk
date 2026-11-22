"""Ticket service tests — the current API, on the conftest fixture db."""

import pytest

from helpdesk.models.exceptions import (
    InvalidTicketTypeError,
    ValidationError,
)
from helpdesk.patterns.observer.publisher import TicketEventPublisher
from helpdesk.repositories.staff_repository import StaffRepository
from helpdesk.repositories.ticket_repository import TicketRepository
from helpdesk.services.ticket_service import TicketService


@pytest.fixture
def service(database):
    return TicketService(
        TicketRepository(database),
        StaffRepository(database),
        TicketEventPublisher(),
    )


def make_ticket(service, **overrides):
    payload = {
        "title": "VPN drops every hour",
        "description": "Connection resets at :55 every hour",
        "category": "TECHNICAL",
        "priority": "HIGH",
        "component": "email",
    }
    payload.update(overrides)
    return service.create_ticket(**payload)


def test_create_ticket_returns_persisted_ticket(service):
    ticket = make_ticket(service)

    assert ticket.id == 1
    assert ticket.status == "OPEN"
    assert ticket.category == "TECHNICAL"
    assert ticket.priority == "HIGH"


def test_create_ticket_persists_a_round_trip(service):
    made = make_ticket(service)

    assert service.get_ticket(made.id) == made


def test_create_ticket_rejects_empty_title(service):
    with pytest.raises(ValidationError, match="Title"):
        make_ticket(service, title="   ")


def test_create_ticket_rejects_retired_category(service):
    with pytest.raises(InvalidTicketTypeError):
        make_ticket(service, category="SOFTWARE")


def test_list_tickets_filters_by_status(service):
    make_ticket(service)

    assert service.list_tickets(status="OPEN")
    assert service.list_tickets(status="CLOSED") == []

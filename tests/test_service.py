import pytest
import os
from helpdesk.services.ticket_service import TicketService

@pytest.fixture
def service():
    test_db = "test_helpdesk.db"
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except PermissionError:
            pass
    
    svc = TicketService(db_path=test_db)
    yield svc

def test_create_ticket_success(service):
    ticket_id = service.create_new_ticket("Baslik", "Aciklama")
    assert ticket_id == 1

def test_create_ticket_empty_title(service):
    with pytest.raises(ValueError):
        service.create_new_ticket("", "Aciklama")

def test_update_ticket_status(service):
    ticket_id = service.create_new_ticket("Baslik", "Aciklama")
    result = service.update_ticket_status(ticket_id, "IN_PROGRESS")
    assert result is True

    ticket = service.get_ticket_by_id(ticket_id)
    assert ticket["status"] == "IN_PROGRESS"
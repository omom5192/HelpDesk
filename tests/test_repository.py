import os
import pytest
from helpdesk.repositories.repository import TicketRepository

@pytest.fixture
def temp_db(tmp_path):
    # Veritabani testleri icin gecici veritabani olusturur
    db_file = tmp_path / "test_helpdesk.db"
    return str(db_file)

def test_add_and_get_ticket(temp_db):
    repo = TicketRepository(db_path=temp_db)
    
    # Ornek bir bilet eklenir
    ticket_id = repo.add_ticket(
        title="Test Title",
        description="Test Description",
        priority="HIGH",
        category="IT"
    )
    
    assert ticket_id is not None
    assert ticket_id > 0
    
    # Tum biletler getirilir ve dogrulanir
    tickets = repo.get_all_tickets()
    assert len(tickets) == 1
    assert tickets[0]["title"] == "Test Title"
    assert tickets[0]["priority"] == "HIGH"
    assert tickets[0]["status"] == "Open"
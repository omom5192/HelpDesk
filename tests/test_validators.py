import pytest
from helpdesk.models.exceptions import TicketValidationError, InvalidTicketTypeError
from helpdesk.models.validators import validate_ticket_data
from helpdesk.models.ticket_types import TicketPriority, TicketCategory

def test_validate_ticket_data_success():
    # Gecerli veri girisi testi
    result = validate_ticket_data(
        title="Yazici Arizasi",
        description="Ofisteki yazici kagit sikistiriyor.",
        priority=TicketPriority.HIGH.value,
        category=TicketCategory.HARDWARE.value
    )
    assert result is True

def test_validate_ticket_data_empty_title():
    # Bos baslik testi (TicketValidationError firlatmali)
    with pytest.raises(TicketValidationError):
        validate_ticket_data("", "Aciklama", "High", "Hardware")

def test_validate_ticket_data_invalid_priority():
    # Gecersiz oncelik testi (InvalidTicketTypeError firlatmali)
    with pytest.raises(InvalidTicketTypeError):
        validate_ticket_data("Baslik", "Aciklama", "SuperHigh", "Hardware")
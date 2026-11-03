import pytest
from helpdesk.models.exceptions import (
    TicketValidationError,
    InvalidTicketTypeError,
    TicketNotFoundError
)

def test_exceptions_inheritance():
    # Tum ozel hatalarin Exception sinifindan turefigini kontrol etme
    assert issubclass(TicketValidationError, Exception)
    assert issubclass(InvalidTicketTypeError, Exception)
    assert issubclass(TicketNotFoundError, Exception)

def test_exception_message():
    # Hata mesajinin dogru iletildigini test etme
    error = TicketValidationError("Gecersiz baslik")
    assert str(error) == "Gecersiz baslik"
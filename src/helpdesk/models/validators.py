from .exceptions import TicketValidationError, InvalidTicketTypeError
from .ticket_types import TicketPriority, TicketCategory

def validate_ticket_data(title: str, description: str, priority: str, category: str):
    """
    Bilet verilerinin gecerliligini kontrol eden fonksiyon.
    """
    # Baslik kontrolu
    if not title or not title.strip():
        raise TicketValidationError("Bilet basligi bos birakilamaz.")
    
    # Aciklama kontrolu
    if not description or not description.strip():
        raise TicketValidationError("Bilet aciklamasi bos birakilamaz.")
        
    # Oncelik seviyesi kontrolu
    valid_priorities = [p.value for p in TicketPriority]
    if priority not in valid_priorities:
        raise InvalidTicketTypeError(f"Gecersiz oncelik seviyesi '{priority}'. Gecerli secenekler: {valid_priorities}")

    # Kategori kontrolu
    valid_categories = [c.value for c in TicketCategory]
    if category not in valid_categories:
        raise InvalidTicketTypeError(f"Gecersiz kategori '{category}'. Gecerli secenekler: {valid_categories}")

    return True
class HelpDeskException(Exception):
    """Base exception for HelpDesk system"""
    pass

class InvalidTicketTypeError(HelpDeskException):
    """Raised when an invalid ticket type or priority is provided"""
    pass

class TicketValidationError(HelpDeskException):
    """Raised when ticket data validation fails"""
    pass

class TicketNotFoundError(HelpDeskException):
    """Raised when a ticket is not found in the system"""
    pass
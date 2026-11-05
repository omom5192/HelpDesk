<<<<<<< HEAD
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
=======
﻿"""Domain exceptions used by HelpDesk."""


class DomainError(Exception):
    """Base exception for business-rule errors."""


class ValidationError(DomainError):
    """Raised when input or model data is invalid."""


class NotFoundError(DomainError):
    """Raised when a requested entity does not exist."""
>>>>>>> d6f5ce911c39ccb1cb20d24fecdc72beb2b8212c

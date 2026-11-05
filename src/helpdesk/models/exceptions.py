"""Domain exceptions used by HelpDesk."""


class DomainError(Exception):
    """Base exception for all HelpDesk domain errors."""


# Backward compatibility with the original exception names.
HelpDeskException = DomainError


class ValidationError(DomainError):
    """Raised when input or model data is invalid."""


class TicketValidationError(ValidationError):
    """Raised when ticket data validation fails."""


class InvalidTicketTypeError(TicketValidationError):
    """Raised when an invalid ticket type or priority is provided."""


class NotFoundError(DomainError):
    """Raised when a requested entity does not exist."""


class TicketNotFoundError(NotFoundError):
    """Raised when a ticket is not found in the system."""

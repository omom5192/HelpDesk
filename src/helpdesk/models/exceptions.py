"""Domain exception hierarchy.

Rejected operations raise these exceptions with human-readable explanations.
The CLI prints the messages verbatim - the domain layer never prints.
"""


class HelpDeskError(Exception):
    """Base class for all application-caused errors."""


class HelpDeskException(HelpDeskError):
    """Backward-compatible alias for the original base exception name."""


class ValidationError(HelpDeskError):
    """An input value violates a business validation rule."""


class DomainError(HelpDeskError):
    """An operation violates a business rule."""


class InvalidTransitionError(DomainError):
    """A lifecycle transition is not allowed; the message explains why."""


class RepositoryError(HelpDeskError):
    """A persistence-layer failure."""


class NotFoundError(RepositoryError):
    """A referenced entity does not exist."""


class TicketValidationError(ValidationError):
    """Raised when ticket data validation fails."""


class InvalidTicketTypeError(TicketValidationError):
    """Raised when an invalid ticket type or priority is provided."""


class TicketNotFoundError(NotFoundError):
    """Raised when a ticket is not found in the system."""

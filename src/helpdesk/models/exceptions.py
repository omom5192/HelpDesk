"""Domain exceptions used by HelpDesk."""


class DomainError(Exception):
    """Base exception for business-rule errors."""


class ValidationError(DomainError):
    """Raised when input or model data is invalid."""


class NotFoundError(DomainError):
    """Raised when a requested entity does not exist."""

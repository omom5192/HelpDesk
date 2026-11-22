"""Shared input validation helpers (BR-6/BR-9).

Validation is lenient on input casing/whitespace but strict on storage:
callers always receive canonical uppercase tokens.
"""

from helpdesk.models.exceptions import InvalidTicketTypeError, TicketValidationError, ValidationError
from helpdesk.models.ticket_types import (
    TICKET_CATEGORIES,
    TICKET_PRIORITIES,
)


def validate_title(title: str) -> str:
    """Title must be 3-120 characters after trimming."""
    trimmed = (title or "").strip()
    if not 3 <= len(trimmed) <= 120:
        raise ValidationError("Title must be 3-120 characters.")
    return trimmed


def validate_description(description: str) -> str:
    """Description must be at least 10 characters after trimming."""
    trimmed = (description or "").strip()
    if len(trimmed) < 10:
        raise ValidationError("Description must be at least 10 characters.")
    return trimmed


def validate_resolution_note(note: str) -> str:
    """BR-3: resolving requires a real note (min 3 chars)."""
    trimmed = (note or "").strip()
    if len(trimmed) < 3:
        raise ValidationError(
            "A resolution note (min 3 chars) is required to resolve."
        )
    return trimmed


def validate_category(value: str) -> str:
    """Canonicalize a category to one of the schema tokens."""
    if not isinstance(value, str):
        raise ValidationError(f"Category must be text, got {type(value).__name__}.")
    canonical = value.strip().upper()
    if canonical not in TICKET_CATEGORIES:
        raise ValidationError(
            f"Category must be one of: {', '.join(TICKET_CATEGORIES)}"
        )
    return canonical


def validate_priority(value: str) -> str:
    """Canonicalize a priority to one of the schema tokens."""
    if not isinstance(value, str):
        raise ValidationError(f"Priority must be text, got {type(value).__name__}.")
    canonical = value.strip().upper()
    if canonical not in TICKET_PRIORITIES:
        raise ValidationError(
            f"Priority must be one of: {', '.join(TICKET_PRIORITIES)}"
        )
    return canonical


def validate_ticket_data(
    title: str,
    description: str,
    priority: str,
    category: str,
) -> bool:
    """Validate all ticket input data (backward-compatible helper)."""
    if not title or not title.strip():
        raise TicketValidationError("Ticket title cannot be empty.")
    if not description or not description.strip():
        raise TicketValidationError("Ticket description cannot be empty.")
    try:
        validate_priority(priority)
        validate_category(category)
    except ValidationError as exc:
        raise InvalidTicketTypeError(str(exc)) from exc
    return True

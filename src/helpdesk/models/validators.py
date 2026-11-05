
from .exceptions import TicketValidationError, InvalidTicketTypeError
from .ticket_types import TicketPriority, TicketCategory


def _validate_enum_value(value: str, enum_class, field_name: str) -> str:
    """Validate an enum value and return its canonical string value."""

    if not isinstance(value, str):
        raise InvalidTicketTypeError(
            f"{field_name} must be a string."
        )

    normalized = value.strip().casefold()

    for item in enum_class:
        # Accept both enum values ("Medium") and enum names ("MEDIUM").
        if normalized in (item.value.casefold(), item.name.casefold()):
            return item.value

    valid_options = [item.value for item in enum_class]

    raise InvalidTicketTypeError(
        f"Invalid {field_name}: '{value}'. "
        f"Valid options: {valid_options}"
    )


def validate_priority(priority: str) -> str:
    """Validate a ticket priority."""
    return _validate_enum_value(
        priority, TicketPriority, "priority"
    )


def validate_category(category: str) -> str:
    """Validate a ticket category."""
    return _validate_enum_value(
        category, TicketCategory, "category"
    )


def validate_ticket_data(
    title: str,
    description: str,
    priority: str,
    category: str,
) -> bool:
    """Validate all ticket input data."""

    if not title or not title.strip():
        raise TicketValidationError(
            "Ticket title cannot be empty."
        )

    if not description or not description.strip():
        raise TicketValidationError(
            "Ticket description cannot be empty."
        )

    validate_priority(priority)
    validate_category(category)

    return True

"""Week-3 hardening: validation edge cases (BR-6/BR-9)."""

import pytest

from helpdesk.models.exceptions import ValidationError
from helpdesk.models.validators import (
    validate_category,
    validate_description,
    validate_priority,
    validate_resolution_note,
    validate_title,
)


@pytest.mark.parametrize("title", ["ab", "", "   ", "x" * 121, None])
def test_title_edges_are_rejected(title):
    with pytest.raises(ValidationError, match="Title"):
        validate_title(title)


@pytest.mark.parametrize("title", ["abc", "x" * 120])
def test_title_boundaries_are_accepted(title):
    assert validate_title(title) == title


def test_title_is_trimmed():
    assert validate_title("  Valid title  ") == "Valid title"


@pytest.mark.parametrize("description", ["", "short", "123456789", None])
def test_short_descriptions_are_rejected(description):
    with pytest.raises(ValidationError, match="Description"):
        validate_description(description)


def test_description_of_ten_characters_is_accepted_and_trimmed():
    assert validate_description("  0123456789  ") == "0123456789"


@pytest.mark.parametrize("note", ["", "  ", "ab", None])
def test_resolution_note_edges_are_rejected(note):
    with pytest.raises(ValidationError, match="resolution note"):
        validate_resolution_note(note)


def test_resolution_note_is_trimmed():
    assert validate_resolution_note("  Fixed it  ") == "Fixed it"


def test_priority_accepts_lower_and_mixed_case():
    assert validate_priority("critical") == "CRITICAL"
    assert validate_priority(" High ") == "HIGH"


@pytest.mark.parametrize("value", ["urgent", "", 3, None])
def test_priority_rejects_unknown_and_non_text_values(value):
    with pytest.raises(ValidationError, match="Priority"):
        validate_priority(value)


def test_category_accepts_lower_case_and_trims():
    assert validate_category(" hardware ") == "HARDWARE"


@pytest.mark.parametrize("value", ["SOFTWARE", "", 7])
def test_category_rejects_unknown_and_non_text_values(value):
    with pytest.raises(ValidationError, match="Category"):
        validate_category(value)

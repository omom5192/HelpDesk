"""Factory Method: creators, registry, and category-specific products."""

from datetime import UTC, datetime

import pytest

from helpdesk.models.exceptions import ValidationError
from helpdesk.models.ticket import AccountTicket, HardwareTicket, TechnicalTicket, Ticket
from helpdesk.patterns.factory import CREATOR_REGISTRY, TicketCreator
from helpdesk.patterns.factory.account_creator import AccountTicketCreator
from helpdesk.patterns.factory.hardware_creator import HardwareTicketCreator
from helpdesk.patterns.factory.technical_creator import TechnicalTicketCreator

NOW = datetime(2026, 11, 2, 9, 0, tzinfo=UTC)


def create(creator, **overrides):
    payload = dict(
        title="Valid ticket title",
        description="A sufficiently long ticket description.",
        deadline=None,
        created_at=NOW,
    )
    payload.update(overrides)
    return creator.create(**payload)


def test_registry_exposes_exactly_the_three_categories():
    assert set(CREATOR_REGISTRY) == {"TECHNICAL", "ACCOUNT", "HARDWARE"}


def test_registry_values_are_creators():
    assert all(isinstance(creator, TicketCreator) for creator in CREATOR_REGISTRY.values())


def test_technical_creator_builds_technical_product():
    ticket = create(CREATOR_REGISTRY["TECHNICAL"], component="email")
    assert isinstance(ticket, TechnicalTicket)
    assert ticket.category == "TECHNICAL"
    assert ticket.component == "email"


def test_technical_creator_defaults_to_medium_priority():
    assert create(CREATOR_REGISTRY["TECHNICAL"], component="network").priority == "MEDIUM"


def test_technical_component_is_case_insensitive_but_stored_lowercase():
    ticket = create(CREATOR_REGISTRY["TECHNICAL"], component="NETWORK")
    assert ticket.component == "network"


def test_technical_component_is_mandatory():
    with pytest.raises(ValidationError, match="'component' is required"):
        create(CREATOR_REGISTRY["TECHNICAL"])


def test_technical_component_must_be_from_the_whitelist():
    with pytest.raises(ValidationError, match="unknown"):
        create(CREATOR_REGISTRY["TECHNICAL"], component="carrier_pigeon")


def test_account_creator_builds_account_product():
    ticket = create(CREATOR_REGISTRY["ACCOUNT"], affected_account="s2026001")
    assert isinstance(ticket, AccountTicket)
    assert ticket.affected_account == "s2026001"


def test_account_creator_defaults_to_high_priority():
    ticket = create(CREATOR_REGISTRY["ACCOUNT"], affected_account="registrar.office")
    assert ticket.priority == "HIGH"


def test_account_field_is_mandatory():
    with pytest.raises(ValidationError, match="'affected_account' is required"):
        create(CREATOR_REGISTRY["ACCOUNT"])


@pytest.mark.parametrize("account", ["ab c!", "café", "@user"])
def test_account_field_rejects_invalid_usernames(account):
    with pytest.raises(ValidationError, match="username pattern"):
        create(CREATOR_REGISTRY["ACCOUNT"], affected_account=account)


def test_hardware_creator_builds_hardware_product():
    ticket = create(
        CREATOR_REGISTRY["HARDWARE"], asset_tag="PC-1234", location="Lab 2"
    )
    assert isinstance(ticket, HardwareTicket)
    assert ticket.asset_tag == "PC-1234"
    assert ticket.location == "Lab 2"


def test_hardware_creator_defaults_to_low_priority():
    ticket = create(
        CREATOR_REGISTRY["HARDWARE"], asset_tag="pc-1234", location="Lab 2"
    )
    assert ticket.priority == "LOW"
    assert ticket.asset_tag == "PC-1234"  # canonical uppercase


def test_hardware_asset_tag_is_mandatory():
    with pytest.raises(ValidationError, match="'asset_tag' is required"):
        create(CREATOR_REGISTRY["HARDWARE"], location="Lab 2")


def test_hardware_location_is_mandatory():
    with pytest.raises(ValidationError, match="'location' is required"):
        create(CREATOR_REGISTRY["HARDWARE"], asset_tag="PC-1234")


def test_hardware_asset_tag_must_match_the_pattern():
    with pytest.raises(ValidationError, match="PC-"):
        create(
            CREATOR_REGISTRY["HARDWARE"], asset_tag="LAPTOP-1", location="Lab 2"
        )


def test_priority_is_canonicalized_by_creators():
    ticket = create(CREATOR_REGISTRY["TECHNICAL"], component="email", priority="high")
    assert ticket.priority == "HIGH"


def test_invalid_priority_is_rejected_by_creators():
    with pytest.raises(ValidationError, match="Priority must be one of"):
        create(CREATOR_REGISTRY["TECHNICAL"], component="email", priority="URGENT")


def test_products_share_the_ticket_base_class():
    for ticket in (
        create(CREATOR_REGISTRY["TECHNICAL"], component="email"),
        create(CREATOR_REGISTRY["ACCOUNT"], affected_account="s1"),
        create(CREATOR_REGISTRY["HARDWARE"], asset_tag="PC-1000", location="Lab"),
    ):
        assert isinstance(ticket, Ticket)


def test_products_add_category_specific_behavior():
    technical = create(CREATOR_REGISTRY["TECHNICAL"], component="database")
    assert technical.escalation_level() == ("DATABASE_ADMIN", "INFRASTRUCTURE_LEAD")

    account = create(
        CREATOR_REGISTRY["ACCOUNT"],
        affected_account="s1",
        description="User is locked out after too many attempts",
    )
    assert account.is_lockout() is True

    hardware = create(
        CREATOR_REGISTRY["HARDWARE"], asset_tag="PC-9999", location="Lab"
    )
    assert hardware.is_warranty_eligible() is True


def test_account_is_lockout_uses_word_boundaries():
    ticket = create(
        AccountTicketCreator(),
        affected_account="s1",
        description="The account is unblocked and working now",
    )
    assert ticket.is_lockout() is False


def test_creator_base_class_is_abstract():
    with pytest.raises(TypeError):
        TicketCreator()


def test_adding_a_creator_does_not_change_the_service():
    """Open/Closed: registering one extra creator is a one-line change."""
    class DemoCreator(TicketCreator):
        category = "DEMO"

        def create(self, *, title, description, deadline, created_at, **fields):
            return Ticket(
                title=title, description=description, category="DEMO",
                created_at=created_at, deadline=deadline,
            )

    original = dict(CREATOR_REGISTRY)
    try:
        CREATOR_REGISTRY["DEMO"] = DemoCreator()
        assert "DEMO" in CREATOR_REGISTRY
    finally:
        CREATOR_REGISTRY.clear()
        CREATOR_REGISTRY.update(original)

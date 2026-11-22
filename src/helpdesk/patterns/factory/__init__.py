"""Factory Method (GoF: Creational) - creator registry.

The ONLY public entry point consumers should import. Keys are category
codes; adding a category = new creator class + one line here (the
Open/Closed payoff).
"""

from helpdesk.patterns.factory.abstract_creator import TicketCreator
from helpdesk.patterns.factory.account_creator import AccountTicketCreator
from helpdesk.patterns.factory.hardware_creator import HardwareTicketCreator
from helpdesk.patterns.factory.technical_creator import TechnicalTicketCreator

CREATOR_REGISTRY: dict[str, TicketCreator] = {
    "TECHNICAL": TechnicalTicketCreator(),
    "ACCOUNT": AccountTicketCreator(),
    "HARDWARE": HardwareTicketCreator(),
}

__all__ = ["CREATOR_REGISTRY", "TicketCreator"]

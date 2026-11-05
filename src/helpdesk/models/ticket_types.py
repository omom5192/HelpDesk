from enum import Enum

class TicketPriority(Enum):
    """Bilet oncelik seviyeleri"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class TicketCategory(Enum):
    """Bilet kategori ve sorun turleri"""
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    NETWORK = "Network"
    ACCESS_REQUEST = "Access Request"
    OTHER = "Other"
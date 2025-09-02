from enum import Enum


class BedStatus(str, Enum):
    AVAILABLE = 'AVAILABLE'
    OCCUPIED = 'OCCUPIED'
    MAINTENANCE = 'MAINTENANCE'
    RESERVED = 'RESERVED'
    UNAVAILABLE = 'UNAVAILABLE'

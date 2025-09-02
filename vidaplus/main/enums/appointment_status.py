from enum import Enum


class AppointmentStatus(str, Enum):
    SCHEDULED = 'SCHEDULED'
    CANCELED = 'CANCELED'
    CONCLUDED = 'CONCLUDED'
    MISSED = 'MISSED'

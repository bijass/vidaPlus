from enum import Enum


class AppointmentTypes(str, Enum):
    CONSULTATION = 'CONSULTATION'
    EXAM = 'EXAM'
    TELEMEDICINE = 'TELEMEDICINE'

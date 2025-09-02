from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from vidaplus.main.enums.appointment_status import AppointmentStatus
from vidaplus.main.enums.appointment_types import AppointmentTypes


class CreateAppointmentSchema(BaseModel):
    patient_id: UUID
    professional_id: UUID
    date_time: datetime
    type: AppointmentTypes
    status: AppointmentStatus
    estimated_duration: int
    location: str
    notes: str

    model_config = ConfigDict(from_attributes=True)


class AppointmentSchema(CreateAppointmentSchema):
    id: int
    created_at: datetime
    updated_at: datetime

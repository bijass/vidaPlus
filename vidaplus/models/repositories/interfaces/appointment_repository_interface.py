from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID

from vidaplus.main.schemas.appointment import AppointmentSchema, CreateAppointmentSchema


class AppointmentRepositoryInterface(ABC):
    @abstractmethod
    def create(self, new_appointment: CreateAppointmentSchema) -> AppointmentSchema:
        pass

    @abstractmethod
    def get(  # noqa: PLR0913
        self,
        patient_id: Optional[UUID] = None,
        professional_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[AppointmentSchema]:
        pass

    @abstractmethod
    def update(self, appointment_id: int, appointment: CreateAppointmentSchema) -> AppointmentSchema:
        pass

    @abstractmethod
    def get_by_id(self, appointment_id: int) -> AppointmentSchema | None:
        pass

    @abstractmethod
    def cancel(self, appointment_id: int) -> None:
        pass

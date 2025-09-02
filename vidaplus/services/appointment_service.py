from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from vidaplus.main.enums.roles import Roles
from vidaplus.main.exceptions import (
    AppointmentNotFountError,
    PermissionRequiredError,
    SchedulingInPastError,
    SchedulingTimeConflictError,
)
from vidaplus.main.schemas.appointment import AppointmentSchema, CreateAppointmentSchema
from vidaplus.main.schemas.user import PublicUserSchema
from vidaplus.models.repositories.interfaces.appointment_repository_interface import AppointmentRepositoryInterface


class AppointmentService:
    def __init__(self, repository: AppointmentRepositoryInterface) -> None:
        self.repository = repository

    def create(self, appointment: CreateAppointmentSchema, creator: PublicUserSchema) -> AppointmentSchema:
        if appointment.patient_id != creator.id and creator.role == Roles.PATIENT:
            raise PermissionRequiredError()

        if not appointment.date_time > datetime.now():
            raise SchedulingInPastError()

        if self.has_time_conflict(appointment.professional_id, appointment.date_time, appointment.estimated_duration):
            raise SchedulingTimeConflictError()

        return self.repository.create(appointment)

    def get(  # noqa: PLR0913
        self,
        patient_id: Optional[UUID] = None,
        professional_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[AppointmentSchema]:
        return self.repository.get(
            patient_id=patient_id,
            professional_id=professional_id,
            start_date=start_date,
            end_date=end_date,
            type=type,
            status=status,
        )

    def cancel(self, appointment_id: int, user: PublicUserSchema) -> None:
        appointment = self.repository.get_by_id(appointment_id)

        if not appointment:
            raise AppointmentNotFountError()

        if appointment.patient_id != user.id and user.role == Roles.PATIENT:
            raise PermissionRequiredError()

        self.repository.cancel(appointment_id)

    def update(
        self, appointment_id: int, appointment: CreateAppointmentSchema, user: PublicUserSchema
    ) -> AppointmentSchema:
        appointment_to_update = self.repository.get_by_id(appointment_id)

        if not appointment_to_update:
            raise AppointmentNotFountError()

        if appointment_to_update.patient_id != user.id and user.role == Roles.PATIENT:
            raise PermissionRequiredError()

        if appointment_to_update.date_time < datetime.now():
            raise SchedulingInPastError()

        if self.has_time_conflict(
            appointment_to_update.professional_id, appointment.date_time, appointment.estimated_duration
        ):
            raise SchedulingTimeConflictError()

        return self.repository.update(appointment_id, appointment)

    def has_time_conflict(self, professional_id: UUID, appointment_start: datetime, duration: int) -> bool:
        appointment_end = appointment_start + timedelta(minutes=duration)
        existing_appointments = self.repository.get(professional_id=professional_id)

        for existing_appointment in existing_appointments:
            existing_appointment_start = existing_appointment.date_time
            existing_appointment_end = existing_appointment_start + timedelta(
                minutes=existing_appointment.estimated_duration
            )

            if (appointment_start <= existing_appointment_start) and (appointment_end >= existing_appointment_end):
                return True

        return False

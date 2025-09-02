from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select

from vidaplus.main.enums.appointment_status import AppointmentStatus
from vidaplus.main.exceptions import AppointmentNotFountError
from vidaplus.main.schemas.appointment import AppointmentSchema, CreateAppointmentSchema
from vidaplus.models.config.connection import DatabaseConnectionHandler
from vidaplus.models.entities.appointment import Appointment
from vidaplus.models.repositories.interfaces.appointment_repository_interface import AppointmentRepositoryInterface


class AppointmentRepository(AppointmentRepositoryInterface):
    def create(self, new_appointment: CreateAppointmentSchema) -> AppointmentSchema:
        with DatabaseConnectionHandler() as db:
            try:
                appointment = Appointment(**new_appointment.model_dump())
                db.session.add(appointment)
                db.session.commit()
                db.session.refresh(appointment)
                return AppointmentSchema.model_validate(appointment)
            except Exception as e:
                db.session.rollback()
                raise e

    def get(  # noqa: PLR0913
        self,
        patient_id: Optional[UUID] = None,
        professional_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[AppointmentSchema]:
        query = select(Appointment)

        if patient_id:
            query = query.filter(Appointment.patient_id == patient_id)

        if professional_id:
            query = query.filter(Appointment.professional_id == professional_id)

        if start_date:
            query = query.filter(Appointment.date_time > start_date)

        if end_date:
            query = query.filter(Appointment.date_time < end_date)

        if type:
            query = query.filter(Appointment.type == type)

        if status:
            query = query.filter(Appointment.status == status)

        with DatabaseConnectionHandler() as db:
            try:
                appointments = db.session.scalars(query).all()
                return [AppointmentSchema.model_validate(appointment) for appointment in appointments]
            except Exception as e:
                db.session.rollback()
                raise e

    def update(self, appointment_id: int, appointment: CreateAppointmentSchema) -> AppointmentSchema:
        with DatabaseConnectionHandler() as db:
            try:
                appointment_db = db.session.get(Appointment, appointment_id)

                for key, value in appointment.model_dump().items():
                    setattr(appointment_db, key, value)

                db.session.commit()
                db.session.refresh(appointment_db)

                return AppointmentSchema.model_validate(appointment_db)
            except Exception as e:
                db.session.rollback()
                raise e

    def get_by_id(self, appointment_id: int) -> AppointmentSchema | None:
        with DatabaseConnectionHandler() as db:
            try:
                appointment = db.session.get(Appointment, appointment_id)
                return AppointmentSchema.model_validate(appointment) if appointment else None
            except Exception as e:
                db.session.rollback()
                raise e

    def cancel(self, appointment_id: int) -> None:
        with DatabaseConnectionHandler() as db:
            try:
                appointment = self.get_by_id(appointment_id)

                if not appointment:
                    raise AppointmentNotFountError()

                appointment.status = AppointmentStatus.CANCELED
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e

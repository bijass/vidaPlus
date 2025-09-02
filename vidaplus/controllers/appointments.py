from datetime import datetime
from http import HTTPStatus
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends

from vidaplus.main.schemas.appointment import AppointmentSchema, CreateAppointmentSchema
from vidaplus.main.schemas.user import PublicUserSchema
from vidaplus.models.repositories.appointment_repository import AppointmentRepository
from vidaplus.services.appointment_service import AppointmentService
from vidaplus.services.auth_service import AuthService

router = APIRouter(prefix='/api/agendamentos', tags=['Agendamentos'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=AppointmentSchema)
def create_appointment(
    data: CreateAppointmentSchema, creator: PublicUserSchema = Depends(AuthService.get_current_user)
) -> AppointmentSchema:
    repository = AppointmentRepository()
    service = AppointmentService(repository)
    return service.create(data, creator)


@router.get('/', status_code=HTTPStatus.OK, response_model=list[AppointmentSchema])
def get_appointments(  # noqa: PLR0913
    patient_id: Optional[UUID] = None,
    professional_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
) -> list[AppointmentSchema]:
    repository = AppointmentRepository()
    service = AppointmentService(repository)
    return service.get(
        patient_id=patient_id,
        professional_id=professional_id,
        start_date=start_date,
        end_date=end_date,
        type=type,
        status=status,
    )


@router.delete('/{appointment_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_appointment(appointment_id: int, user: PublicUserSchema = Depends(AuthService.get_current_user)) -> None:
    repository = AppointmentRepository()
    service = AppointmentService(repository)
    service.cancel(appointment_id, user)


@router.put('/{appointment_id}', status_code=HTTPStatus.OK, response_model=AppointmentSchema)
def update_appointment(
    appointment_id: int,
    data: CreateAppointmentSchema,
    user: PublicUserSchema = Depends(AuthService.get_current_user),
) -> AppointmentSchema:
    repository = AppointmentRepository()
    service = AppointmentService(repository)
    return service.update(appointment_id, data, user)

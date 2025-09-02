from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends

from vidaplus.main.enums.roles import Roles
from vidaplus.main.schemas.appointment import AppointmentSchema
from vidaplus.main.schemas.user import CreateUserSchema, PublicUserSchema, RequestCreateUserSchema
from vidaplus.models.repositories.appointment_repository import AppointmentRepository
from vidaplus.models.repositories.user_repository import UserRepository
from vidaplus.services.appointment_service import AppointmentService
from vidaplus.services.auth_service import AuthService
from vidaplus.services.user_service import UserService

router = APIRouter(prefix='/api/profissionais', tags=['Profissionais de Saúde'])


@router.post('/', status_code=HTTPStatus.CREATED)
def create_healthcare_professional(
    data: RequestCreateUserSchema, creator: PublicUserSchema = Depends(AuthService.get_current_user)
) -> PublicUserSchema:
    repository = UserRepository()
    service = UserService(repository)
    return service.new_healthcare_professional(data, creator)


@router.get('/', status_code=HTTPStatus.OK, response_model=list[PublicUserSchema])
def get_healthcare_professionals() -> list[PublicUserSchema]:
    repository = UserRepository()
    service = UserService(repository)
    return service.all(Roles.HEALTHCARE_PROFESSIONAL)


@router.get('/{healthcare_professional_id}', status_code=HTTPStatus.OK, response_model=PublicUserSchema)
def get_healthcare_professional(
    healthcare_professional_id: UUID, is_admin: bool = Depends(AuthService.is_admin)
) -> PublicUserSchema:
    repository = UserRepository()
    service = UserService(repository)
    return service.get_by_id(healthcare_professional_id)


@router.put('/{healthcare_professional_id}', status_code=HTTPStatus.OK, response_model=PublicUserSchema)
def update_healthcare_professional(
    healthcare_professional_id: UUID,
    data: CreateUserSchema,
    executor: PublicUserSchema = Depends(AuthService.get_current_user),
) -> PublicUserSchema:
    repository = UserRepository()
    service = UserService(repository)
    return service.update(healthcare_professional_id, data, executor)


@router.delete('/{healthcare_professional_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_healthcare_professional(
    healthcare_professional_id: UUID,
    executor: PublicUserSchema = Depends(AuthService.get_current_user),
) -> None:
    repository = UserRepository()
    service = UserService(repository)
    service.delete(healthcare_professional_id, executor)


@router.get(
    '/{healthcare_professional_id}/agendamentos', status_code=HTTPStatus.OK, response_model=list[AppointmentSchema]
)
def get_healthcare_professional_appointments(
    healthcare_professional_id: UUID,
    current_user: PublicUserSchema = Depends(AuthService.get_current_user),
) -> list[AppointmentSchema]:
    repository = AppointmentRepository()
    service = AppointmentService(repository)
    return service.get(professional_id=healthcare_professional_id)

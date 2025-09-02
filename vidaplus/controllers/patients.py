from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends

from vidaplus.main.enums.roles import Roles
from vidaplus.main.schemas.user import CreateUserSchema, PublicUserSchema, RequestCreateUserSchema
from vidaplus.models.repositories.user_repository import UserRepository
from vidaplus.services.auth_service import AuthService
from vidaplus.services.user_service import UserService

router = APIRouter(prefix='/api/pacientes', tags=['Pacientes'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=PublicUserSchema)
def register_patient(data: RequestCreateUserSchema) -> PublicUserSchema:
    user_repository = UserRepository()
    user_service = UserService(user_repository)
    return user_service.new_patient(data)


@router.get('/', status_code=HTTPStatus.OK, response_model=list[PublicUserSchema])
def list_patients() -> list[PublicUserSchema]:
    user_repository = UserRepository()
    user_service = UserService(user_repository)
    return user_service.all(Roles.PATIENT)


@router.get('/{patient_id}', status_code=HTTPStatus.OK, response_model=PublicUserSchema)
def get_patient(patient_id: UUID) -> PublicUserSchema:
    user_repository = UserRepository()
    user_service = UserService(user_repository)
    return user_service.get_by_id(patient_id)


@router.put('/{patient_id}', status_code=HTTPStatus.OK, response_model=PublicUserSchema)
def update_patient(
    patient_id: UUID, data: CreateUserSchema, executor: PublicUserSchema = Depends(AuthService.get_current_user)
) -> PublicUserSchema:
    user_repository = UserRepository()
    user_service = UserService(user_repository)
    return user_service.update(patient_id, data, executor)


@router.delete('/{patient_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_patient(patient_id: UUID, executor: PublicUserSchema = Depends(AuthService.get_current_user)) -> None:
    user_repository = UserRepository()
    user_service = UserService(user_repository)
    user_service.delete(patient_id, executor)

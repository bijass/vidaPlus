from http import HTTPStatus

from fastapi import APIRouter, Depends

from vidaplus.main.schemas.unit import CreateUnitSchema, UnitSchema
from vidaplus.main.schemas.user import PublicUserSchema
from vidaplus.models.repositories.unit_repository import UnitRepository
from vidaplus.services.auth_service import AuthService
from vidaplus.services.unit_service import UnitService

router = APIRouter(prefix='/api/unidades', tags=['Unidades'])


@router.get('/', status_code=HTTPStatus.OK, response_model=list[UnitSchema])
def list_units() -> list:
    repository = UnitRepository()
    service = UnitService(repository)
    return service.get_all()


@router.get('/{unit_id}', status_code=HTTPStatus.OK, response_model=UnitSchema | None)
def get_unit(unit_id: int) -> UnitSchema | None:
    repository = UnitRepository()
    service = UnitService(repository)
    return service.get_by_id(unit_id)


@router.post('/', status_code=HTTPStatus.CREATED)
def create_unit(
    payload: CreateUnitSchema, creator: PublicUserSchema = Depends(AuthService.get_current_user)
) -> UnitSchema:
    repository = UnitRepository()
    service = UnitService(repository)
    return service.create(payload, creator)


@router.put('/{unit_id}', status_code=HTTPStatus.OK, response_model=UnitSchema)
def update_unit(
    unit_id: int, payload: CreateUnitSchema, executor: PublicUserSchema = Depends(AuthService.get_current_user)
) -> UnitSchema:
    repository = UnitRepository()
    service = UnitService(repository)
    return service.update(unit_id, payload, executor)


@router.delete('/{unit_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_unit(unit_id: int, executor: PublicUserSchema = Depends(AuthService.get_current_user)) -> None:
    repository = UnitRepository()
    service = UnitService(repository)
    service.delete(unit_id, executor)

from http import HTTPStatus

from fastapi import APIRouter, Depends

from vidaplus.main.schemas.supply import CreateSupplySchema, SupplySchema
from vidaplus.main.schemas.user import PublicUserSchema
from vidaplus.models.repositories.supply_repository import SupplyRepository
from vidaplus.services.auth_service import AuthService
from vidaplus.services.supply_service import SupplyService

router = APIRouter(prefix='/api/estoque', tags=['Estoque'])
repository = SupplyRepository()
service = SupplyService(repository)


@router.get('/', status_code=HTTPStatus.OK, response_model=list[SupplySchema])
def get_all_supplies() -> list[SupplySchema]:
    return service.all()


@router.get('/{supply_id}', status_code=HTTPStatus.OK, response_model=SupplySchema)
def get_supply_by_id(supply_id: int) -> SupplySchema:
    return service.get_by_id(supply_id)


@router.post('/', status_code=HTTPStatus.CREATED, response_model=SupplySchema)
def create_supply(
    supply: CreateSupplySchema, creator: PublicUserSchema = Depends(AuthService.get_current_user)
) -> SupplySchema:
    return service.create(supply, creator)


@router.put('/{supply_id}', status_code=HTTPStatus.OK, response_model=SupplySchema)
def update_supply(
    supply_id: int, supply: CreateSupplySchema, executor: PublicUserSchema = Depends(AuthService.get_current_user)
) -> SupplySchema:
    return service.update(supply_id, supply, executor)


@router.delete('/{supply_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_supply(supply_id: int, executor: PublicUserSchema = Depends(AuthService.get_current_user)) -> None:
    service.delete(supply_id, executor)

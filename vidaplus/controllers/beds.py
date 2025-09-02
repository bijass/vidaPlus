from http import HTTPStatus

from fastapi import APIRouter, Depends

from vidaplus.main.schemas.bed import BedSchema, CreateBedSchema
from vidaplus.main.schemas.user import PublicUserSchema
from vidaplus.models.repositories.bed_repository import BedRepository
from vidaplus.models.repositories.unit_repository import UnitRepository
from vidaplus.services.auth_service import AuthService
from vidaplus.services.bed_service import BedService

router = APIRouter(prefix='/api/leitos', tags=['Leitos'])


@router.get('/', status_code=HTTPStatus.OK, response_model=list[BedSchema])
def get_beds() -> list[BedSchema]:
    bed_repo = BedRepository()
    unit_repo = UnitRepository()
    service = BedService(bed_repo, unit_repo)
    return service.all()


@router.get('/{bed_id}', status_code=HTTPStatus.OK, response_model=BedSchema)
def get_bed(bed_id: int) -> BedSchema:
    bed_repo = BedRepository()
    unit_repo = UnitRepository()
    service = BedService(bed_repo, unit_repo)
    return service.get_by_id(bed_id)


@router.post('/', status_code=HTTPStatus.CREATED, response_model=BedSchema)
def create_bed(bed: CreateBedSchema, creator: PublicUserSchema = Depends(AuthService.get_current_user)) -> BedSchema:
    bed_repo = BedRepository()
    unit_repo = UnitRepository()
    service = BedService(bed_repo, unit_repo)
    return service.create(bed, creator)


@router.put('/{bed_id}', status_code=HTTPStatus.OK, response_model=BedSchema)
def update_bed(
    bed_id: int, bed: CreateBedSchema, executor: PublicUserSchema = Depends(AuthService.get_current_user)
) -> BedSchema:
    bed_repo = BedRepository()
    unit_repo = UnitRepository()
    service = BedService(bed_repo, unit_repo)
    return service.update(bed_id, bed, executor)


@router.delete('/{bed_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_bed(bed_id: int, executor: PublicUserSchema = Depends(AuthService.get_current_user)) -> None:
    bed_repo = BedRepository()
    unit_repo = UnitRepository()
    service = BedService(bed_repo, unit_repo)
    service.delete(bed_id, executor)

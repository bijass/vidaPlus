from vidaplus.main.enums.roles import Roles
from vidaplus.main.exceptions import BedNotFoundError, PermissionRequiredError, UnitNotFoundError
from vidaplus.main.schemas.bed import BedSchema, CreateBedSchema
from vidaplus.main.schemas.user import PublicUserSchema
from vidaplus.models.repositories.interfaces.bed_repository_interface import BedRepositoryInterface
from vidaplus.models.repositories.interfaces.unit_repository_interface import UnitRepositoryInterface


class BedService:
    def __init__(self, bed_repository: BedRepositoryInterface, unit_repository: UnitRepositoryInterface) -> None:
        self.bed_repository = bed_repository
        self.unit_repository = unit_repository

    def create(self, bed: CreateBedSchema, creator: PublicUserSchema) -> BedSchema:
        if not creator.role == Roles.ADMIN:
            raise PermissionRequiredError()

        unit = self.unit_repository.get_by_id(bed.unit_id)

        if not unit:
            raise UnitNotFoundError()

        return self.bed_repository.create(bed)

    def all(self) -> list[BedSchema]:
        return self.bed_repository.all()

    def get_by_id(self, bed_id: int) -> BedSchema:
        bed = self.bed_repository.get_by_id(bed_id)

        if not bed:
            raise BedNotFoundError()

        return bed

    def update(self, bed_id: int, bed: CreateBedSchema, executor: PublicUserSchema) -> BedSchema:
        if not executor.role == Roles.ADMIN:
            raise PermissionRequiredError()

        unit = self.unit_repository.get_by_id(bed.unit_id)
        if not unit:
            raise UnitNotFoundError()

        return self.bed_repository.update(bed_id, bed)

    def delete(self, bed_id: int, executor: PublicUserSchema) -> None:
        if not executor.role == Roles.ADMIN:
            raise PermissionRequiredError()

        bed = self.bed_repository.get_by_id(bed_id)
        if not bed:
            raise BedNotFoundError()

        return self.bed_repository.delete(bed_id)

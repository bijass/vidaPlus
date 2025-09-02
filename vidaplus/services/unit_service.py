from vidaplus.main.enums.roles import Roles
from vidaplus.main.exceptions import PermissionRequiredError, UnitNotFoundError
from vidaplus.main.schemas.unit import CreateUnitSchema, UnitSchema
from vidaplus.main.schemas.user import PublicUserSchema
from vidaplus.models.repositories.interfaces.unit_repository_interface import UnitRepositoryInterface


class UnitService:
    def __init__(self, repository: UnitRepositoryInterface) -> None:
        self.repository = repository

    def create(self, data: CreateUnitSchema, creator: PublicUserSchema) -> UnitSchema:
        if not creator.role == Roles.ADMIN:
            raise PermissionRequiredError()

        return self.repository.create(data)

    def get_all(self) -> list[UnitSchema]:
        return self.repository.all()

    def get_by_id(self, unit_id: int) -> UnitSchema:
        unit = self.repository.get_by_id(unit_id)

        if not unit:
            raise UnitNotFoundError()

        return unit

    def update(self, unit_id: int, data: CreateUnitSchema, executor: PublicUserSchema) -> UnitSchema:
        unit = self.repository.get_by_id(unit_id)

        if not executor.role == Roles.ADMIN:
            raise PermissionRequiredError()

        if not unit:
            raise UnitNotFoundError()

        return self.repository.update(unit_id, data)

    def delete(self, unit_id: int, executor: PublicUserSchema) -> None:
        if not executor.role == Roles.ADMIN:
            raise PermissionRequiredError()

        unit = self.repository.get_by_id(unit_id)
        if not unit:
            raise UnitNotFoundError()

        return self.repository.delete(unit_id)

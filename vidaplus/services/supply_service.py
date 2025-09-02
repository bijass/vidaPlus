from vidaplus.main.enums.roles import Roles
from vidaplus.main.exceptions import PermissionRequiredError, SupplyNotFoundError
from vidaplus.main.schemas.supply import CreateSupplySchema, SupplySchema
from vidaplus.main.schemas.user import PublicUserSchema
from vidaplus.models.repositories.interfaces.supply_repository_interface import SupplyRepositoryInterface


class SupplyService:
    def __init__(self, supply_repository: SupplyRepositoryInterface) -> None:
        self.supply_repository = supply_repository

    def create(self, data: CreateSupplySchema, creator: PublicUserSchema) -> SupplySchema:
        if not creator.role == Roles.ADMIN:
            raise PermissionRequiredError()

        return self.supply_repository.create(data)

    def all(self) -> list[SupplySchema]:
        return self.supply_repository.all()

    def get_by_id(self, supply_id: int) -> SupplySchema:
        supply = self.supply_repository.get_by_id(supply_id)

        if not supply:
            raise SupplyNotFoundError()

        return supply

    def update(self, supply_id: int, data: CreateSupplySchema, executor: PublicUserSchema) -> SupplySchema:
        if not executor.role == Roles.ADMIN:
            raise PermissionRequiredError()

        supply = self.supply_repository.get_by_id(supply_id)
        if not supply:
            raise SupplyNotFoundError()

        return self.supply_repository.update(supply_id, data)

    def delete(self, supply_id: int, executor: PublicUserSchema) -> None:
        if not executor.role == Roles.ADMIN:
            raise PermissionRequiredError()

        supply = self.supply_repository.get_by_id(supply_id)
        if not supply:
            raise SupplyNotFoundError()

        self.supply_repository.delete(supply_id)

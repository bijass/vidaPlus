from abc import ABC, abstractmethod

from vidaplus.main.schemas.supply import CreateSupplySchema, SupplySchema


class SupplyRepositoryInterface(ABC):
    @abstractmethod
    def create(self, supply: CreateSupplySchema) -> SupplySchema:
        pass

    @abstractmethod
    def all(self) -> list[SupplySchema]:
        pass

    @abstractmethod
    def get_by_id(self, supply_id: int) -> SupplySchema | None:
        pass

    @abstractmethod
    def update(self, supply_id: int, supply: CreateSupplySchema) -> SupplySchema:
        pass

    @abstractmethod
    def delete(self, supply_id: int) -> None:
        pass

from abc import ABC, abstractmethod

from vidaplus.main.schemas.unit import CreateUnitSchema, UnitSchema


class UnitRepositoryInterface(ABC):
    @abstractmethod
    def create(self, unit: CreateUnitSchema) -> UnitSchema:
        pass

    @abstractmethod
    def all(self) -> list[UnitSchema]:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> UnitSchema | None:
        pass

    @abstractmethod
    def update(self, id: int, unit: CreateUnitSchema) -> UnitSchema:
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        pass

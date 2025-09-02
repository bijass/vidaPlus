from abc import ABC, abstractmethod

from vidaplus.main.schemas.bed import BedSchema, CreateBedSchema


class BedRepositoryInterface(ABC):
    @abstractmethod
    def create(self, bed: CreateBedSchema) -> BedSchema:
        pass

    @abstractmethod
    def all(self) -> list[BedSchema]:
        pass

    @abstractmethod
    def get_by_id(self, bed_id: int) -> BedSchema | None:
        pass

    @abstractmethod
    def update(self, bed_id: int, bed: CreateBedSchema) -> BedSchema:
        pass

    @abstractmethod
    def delete(self, bed_id: int) -> None:
        pass

from abc import ABC, abstractmethod

from vidaplus.main.schemas.admission import AdmissionSchema, CreateAdmissionSchema, UpdateAdmissionSchema


class AdmissionRepositoryInterface(ABC):
    @abstractmethod
    def create(self, data: CreateAdmissionSchema) -> AdmissionSchema:
        pass

    @abstractmethod
    def all(self) -> list[AdmissionSchema]:
        pass

    @abstractmethod
    def get_by_id(self, admission_id: int) -> AdmissionSchema | None:
        pass

    @abstractmethod
    def update(self, admission_id: int, data: UpdateAdmissionSchema) -> AdmissionSchema:
        pass

    @abstractmethod
    def delete(self, admission_id: int) -> None:
        pass

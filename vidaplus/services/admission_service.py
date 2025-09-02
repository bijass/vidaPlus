from vidaplus.main.enums.bed_status import BedStatus
from vidaplus.main.enums.roles import Roles
from vidaplus.main.exceptions import (
    AdmissionNotFoundError,
    BedNotAvailableError,
    BedNotFoundError,
    PermissionRequiredError,
    UserNotFoundError,
)
from vidaplus.main.schemas.admission import AdmissionSchema, CreateAdmissionSchema, UpdateAdmissionSchema
from vidaplus.main.schemas.user import PublicUserSchema
from vidaplus.models.repositories.interfaces.admission_repository_interface import AdmissionRepositoryInterface
from vidaplus.models.repositories.interfaces.bed_repository_interface import BedRepositoryInterface
from vidaplus.models.repositories.interfaces.user_repository_interface import UserRepositoryInterface


class AdmissionService:
    def __init__(
        self,
        admission_repository: AdmissionRepositoryInterface,
        user_repository: UserRepositoryInterface,
        bed_repository: BedRepositoryInterface,
    ) -> None:
        self.admission_repository = admission_repository
        self.user_repository = user_repository
        self.bed_repository = bed_repository

    def create(self, admission: CreateAdmissionSchema, creator: PublicUserSchema) -> AdmissionSchema:
        if creator.role not in [Roles.ADMIN, Roles.HEALTHCARE_PROFESSIONAL]:
            raise PermissionRequiredError()

        patient = self.user_repository.get_by_id(admission.patient_id)
        if not patient or not patient.role == Roles.PATIENT:
            raise UserNotFoundError()

        bed = self.bed_repository.get_by_id(admission.bed_id)
        if not bed:
            raise BedNotFoundError()

        if not bed.status == BedStatus.AVAILABLE:
            raise BedNotAvailableError()

        return self.admission_repository.create(admission)

    def all(self) -> list[AdmissionSchema]:
        return self.admission_repository.all()

    def get_by_id(self, admission_id: int) -> AdmissionSchema:
        admission = self.admission_repository.get_by_id(admission_id)

        if not admission:
            raise AdmissionNotFoundError()

        return admission

    def update(self, admission_id: int, data: UpdateAdmissionSchema, executor: PublicUserSchema) -> AdmissionSchema:
        if not executor.role == Roles.ADMIN:
            raise PermissionRequiredError()

        admission = self.admission_repository.get_by_id(admission_id)

        if not admission:
            raise AdmissionNotFoundError()

        return self.admission_repository.update(admission_id, data)

    def delete(self, admission_id: int, executor: PublicUserSchema) -> None:
        if not executor.role == Roles.ADMIN:
            raise PermissionRequiredError()

        admission = self.admission_repository.get_by_id(admission_id)

        if not admission:
            raise AdmissionNotFoundError()

        self.admission_repository.delete(admission_id)

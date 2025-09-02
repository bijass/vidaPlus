from http import HTTPStatus

from fastapi import APIRouter, Depends

from vidaplus.main.schemas.admission import AdmissionSchema, CreateAdmissionSchema, UpdateAdmissionSchema
from vidaplus.main.schemas.user import PublicUserSchema
from vidaplus.models.repositories.admission_repository import AdmissionRepository
from vidaplus.models.repositories.bed_repository import BedRepository
from vidaplus.models.repositories.user_repository import UserRepository
from vidaplus.services.admission_service import AdmissionService
from vidaplus.services.auth_service import AuthService

router = APIRouter(prefix='/api/internacoes', tags=['Internações'])
admission_repository = AdmissionRepository()
user_repository = UserRepository()
bed_repository = BedRepository()
service = AdmissionService(admission_repository, user_repository, bed_repository)


@router.get('/', status_code=HTTPStatus.OK, response_model=list[AdmissionSchema])
def get_all() -> list[AdmissionSchema]:
    return service.all()


@router.get('/{admission_id}', status_code=HTTPStatus.OK, response_model=AdmissionSchema)
def get_by_id(admission_id: int) -> AdmissionSchema:
    return service.get_by_id(admission_id)


@router.post('/', status_code=HTTPStatus.CREATED, response_model=AdmissionSchema)
def create(
    admission: CreateAdmissionSchema, creator: PublicUserSchema = Depends(AuthService.get_current_user)
) -> AdmissionSchema:
    return service.create(admission, creator)


@router.put('/{admission_id}', status_code=HTTPStatus.OK, response_model=AdmissionSchema)
def update(
    admission_id: int,
    admission: UpdateAdmissionSchema,
    executor: PublicUserSchema = Depends(AuthService.get_current_user),
) -> AdmissionSchema:
    return service.update(admission_id, admission, executor)


@router.delete('/{admission_id}', status_code=HTTPStatus.NO_CONTENT)
def delete(admission_id: int, executor: PublicUserSchema = Depends(AuthService.get_current_user)) -> None:
    service.delete(admission_id, executor)

from uuid import UUID

from vidaplus.main.enums.roles import Roles
from vidaplus.main.exceptions import (
    AuthenticationError,
    EmailAlreadyExistsError,
    PermissionRequiredError,
    UserNotFoundError,
)
from vidaplus.main.schemas.user import CreateUserSchema, PublicUserSchema, RequestCreateUserSchema
from vidaplus.models.repositories.interfaces.user_repository_interface import UserRepositoryInterface
from vidaplus.services.auth_service import AuthService


class UserService:
    def __init__(self, repository: UserRepositoryInterface) -> None:
        self.repository = repository

    def new_patient(self, new_user: RequestCreateUserSchema) -> PublicUserSchema:
        try:
            email_already_exists = self.repository.get_by_email(new_user.email)

            if email_already_exists:
                raise EmailAlreadyExistsError()

            user_with_role = CreateUserSchema(**new_user.model_dump(), role=Roles.PATIENT)
            created_user = self.repository.create(user_with_role)
            return PublicUserSchema(**created_user.model_dump())
        except Exception as e:
            raise e

    def new_healthcare_professional(
        self, new_user: RequestCreateUserSchema, creator: PublicUserSchema
    ) -> PublicUserSchema:
        try:
            if not creator.role == Roles.ADMIN:
                raise PermissionRequiredError()

            email_already_exists = self.repository.get_by_email(new_user.email)
            if email_already_exists:
                raise EmailAlreadyExistsError()

            user_with_role = CreateUserSchema(**new_user.model_dump(), role=Roles.HEALTHCARE_PROFESSIONAL)
            created_user = self.repository.create(user_with_role)
            return PublicUserSchema(**created_user.model_dump())
        except Exception as e:
            raise e

    def update(self, user_id: UUID, data: CreateUserSchema, executor: PublicUserSchema) -> PublicUserSchema:
        try:
            user = self.repository.get_by_id(user_id)

            if not user:
                raise UserNotFoundError()

            if not executor.role == Roles.ADMIN and user.id != executor.id:
                raise PermissionRequiredError()

            if not executor.role == Roles.ADMIN and not user.role == data.role:
                raise PermissionRequiredError()

            user = self.repository.update(user_id, data)

            return PublicUserSchema(**user.model_dump())
        except Exception as e:
            raise e

    def delete(self, user_id: UUID, executor: PublicUserSchema) -> None:
        try:
            user = self.repository.get_by_id(user_id)
            if not user:
                raise UserNotFoundError()

            if not executor.role == Roles.ADMIN:
                raise PermissionRequiredError()

            self.repository.delete(user_id)
        except Exception as e:
            raise e

    def authenticate(self, email: str, password: str) -> str:
        user = self.repository.get_by_email(email)

        if not user or not user.verify_password(password):
            raise AuthenticationError()

        public_user = PublicUserSchema(**user.model_dump())
        access_token = AuthService.create_access_token(public_user.model_dump())
        return access_token

    def all(self, role: Roles) -> list[PublicUserSchema]:
        users = self.repository.get_all(role)
        return [PublicUserSchema(**user.model_dump()) for user in users]

    def get_by_id(self, user_id: UUID) -> PublicUserSchema:
        user = self.repository.get_by_id(user_id)

        if not user:
            raise UserNotFoundError()

        return PublicUserSchema(**user.model_dump())

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from vidaplus.main.enums.roles import Roles
from vidaplus.main.schemas.user import CreateUserSchema, UserSchema


class UserRepositoryInterface(ABC):
    @abstractmethod
    def create(self, new_user: CreateUserSchema) -> UserSchema:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> UserSchema | None:
        pass

    @abstractmethod
    def get_all(self, role: Optional[Roles]) -> list[UserSchema]:
        pass

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> UserSchema | None:
        pass

    @abstractmethod
    def update(self, user_id: UUID, user: CreateUserSchema) -> UserSchema:
        pass

    @abstractmethod
    def delete(self, user_id: UUID) -> None:
        pass

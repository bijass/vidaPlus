from typing import Optional
from uuid import UUID

from sqlalchemy import select

from vidaplus.main.enums.roles import Roles
from vidaplus.main.schemas.user import CreateUserSchema, UserSchema
from vidaplus.models.config.connection import DatabaseConnectionHandler
from vidaplus.models.entities.user import User
from vidaplus.models.repositories.interfaces.user_repository_interface import UserRepositoryInterface


class UserRepository(UserRepositoryInterface):
    def create(self, new_user: CreateUserSchema) -> UserSchema:
        with DatabaseConnectionHandler() as db:
            try:
                user = User(**new_user.model_dump())
                db.session.add(user)
                db.session.commit()
                db.session.refresh(user)
                return UserSchema.model_validate(user)
            except Exception as ex:
                db.session.rollback()
                raise ex

    def get_all(self, role: Optional[Roles] = None) -> list[UserSchema]:
        with DatabaseConnectionHandler() as db:
            try:
                query = select(User)

                if role:
                    query = query.filter(User.role == role)

                users = db.session.scalars(query).all()
                return [UserSchema.model_validate(user) for user in users]
            except Exception as ex:
                db.session.rollback()
                raise ex

    def get_by_email(self, email: str) -> UserSchema | None:
        with DatabaseConnectionHandler() as db:
            try:
                user = db.session.scalar(select(User).where(User.email == email))
                return UserSchema.model_validate(user) if user else None
            except Exception as ex:
                db.session.rollback()
                raise ex

    def get_by_id(self, user_id: UUID) -> UserSchema | None:
        with DatabaseConnectionHandler() as db:
            try:
                user = db.session.scalar(select(User).where(User.id == user_id))
                return UserSchema.model_validate(user) if user else None
            except Exception as ex:
                db.session.rollback()
                raise ex

    def update(self, user_id: UUID, user: CreateUserSchema) -> UserSchema:
        with DatabaseConnectionHandler() as db:
            try:
                user_db = db.session.get(User, user_id)

                for k, v in user.model_dump().items():
                    setattr(user_db, k, v)

                db.session.commit()
                db.session.refresh(user_db)

                return UserSchema.model_validate(user_db)
            except Exception as ex:
                db.session.rollback()
                raise ex

    def delete(self, user_id: UUID) -> None:
        with DatabaseConnectionHandler() as db:
            try:
                user = db.session.get(User, user_id)
                db.session.delete(user)
                db.session.commit()
            except Exception as ex:
                db.session.rollback()
                raise ex

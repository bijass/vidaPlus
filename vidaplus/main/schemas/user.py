from datetime import datetime
from uuid import UUID

import bcrypt
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from vidaplus.main.enums.roles import Roles


class RequestCreateUserSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)


class CreateUserSchema(RequestCreateUserSchema):
    role: Roles

    @field_validator('password')
    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


class UserSchema(CreateUserSchema):
    id: UUID
    created_at: datetime

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))


class PublicUserSchema(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: Roles
    created_at: datetime

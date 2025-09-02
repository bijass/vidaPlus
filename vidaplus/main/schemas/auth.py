from datetime import datetime

from pydantic import BaseModel, EmailStr

from vidaplus.main.schemas.user import PublicUserSchema


class TokenData(PublicUserSchema):
    exp: datetime


class RequestAuthUserData(BaseModel):
    email: EmailStr
    password: str


class ResponseAuthToken(BaseModel):
    access_token: str
    token_type: str = 'bearer'

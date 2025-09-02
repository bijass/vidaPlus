from http import HTTPStatus

from fastapi import APIRouter, Depends

from vidaplus.main.schemas.auth import RequestAuthUserData, ResponseAuthToken
from vidaplus.models.repositories.user_repository import UserRepository
from vidaplus.services.auth_service import AuthService
from vidaplus.services.user_service import UserService

router = APIRouter(prefix='/api/auth', tags=['Autenticação'])


@router.post('/token', status_code=HTTPStatus.OK, response_model=ResponseAuthToken)
def get_access_token(data: RequestAuthUserData) -> ResponseAuthToken:
    user_repository = UserRepository()
    user_service = UserService(user_repository)
    access_token = user_service.authenticate(data.email, data.password)
    return ResponseAuthToken(access_token=access_token)


@router.post('/refresh', status_code=HTTPStatus.OK, response_model=ResponseAuthToken)
def refresh_token(access_token: str = Depends(AuthService.oauth2_scheme)) -> ResponseAuthToken:
    new_access_token = AuthService.refresh_token(access_token=access_token)
    return ResponseAuthToken(access_token=new_access_token)

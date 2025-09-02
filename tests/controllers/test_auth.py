from http import HTTPStatus

from fastapi.testclient import TestClient

from vidaplus.main.schemas.user import UserSchema


def test_get_access_token(client: TestClient, patient: UserSchema) -> None:
    data = {
        'email': 'johndoe@example.com',
        'password': 'ilovepotatos',
    }

    response = client.post('/api/auth/token', json=data)
    response_data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()
    assert 'token_type' in response.json()
    assert response_data['token_type'] == 'bearer'
    assert response_data['access_token'] != ''
    assert response_data['access_token'] is not None


def test_get_access_token_with_invalid_credentials(client: TestClient, patient: UserSchema) -> None:
    data = {
        'email': 'invalid_user@invaliddomain.com',
        'password': 'invaid_password',
    }

    response = client.post('/api/auth/token', json=data)
    response_data = response.json()

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response_data['detail'] == 'Email ou senha inválidos'


def test_get_access_token_with_inexistent_user(client: TestClient) -> None:
    data = {
        'email': 'johndoe@example.com',
        'password': 'ilovepotatos',
    }

    response = client.post('/api/auth/token', json=data)
    response_data = response.json()

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response_data['detail'] == 'Email ou senha inválidos'


def test_refresh_access_token(client: TestClient, token: str) -> None:
    response = client.post('/api/auth/refresh', headers={'Authorization': f'Bearer {token}'})

    response_data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response_data
    assert 'token_type' in response_data
    assert response_data['token_type'] == 'bearer'

from http import HTTPStatus
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select

from vidaplus.main.enums.roles import Roles
from vidaplus.main.schemas.user import UserSchema
from vidaplus.models.config.connection import DatabaseConnectionHandler
from vidaplus.models.entities.user import User


def test_register_new_patient(client: TestClient) -> None:
    data = {
        'name': 'John Doe',
        'email': 'johndoe@example.com',
        'password': 'ilovepotatos',
    }

    response = client.post('/api/pacientes', json=data)
    response_data = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert response_data['name'] == data['name']
    assert response_data['email'] == data['email']
    assert 'password' not in response_data
    assert 'role' in response_data
    assert 'id' in response_data
    assert 'created_at' in response_data
    assert response_data['role'] == 'PATIENT'


def test_register_new_patient_with_existing_email(client: TestClient, patient: UserSchema) -> None:
    data = {
        'name': 'John Doe',
        'email': 'johndoe@example.com',
        'password': 'ilovepotatos',
    }

    response = client.post('/api/pacientes', json=data)
    response_data = response.json()

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response_data['detail'] == 'O email já foi cadastrado'


def test_register_new_patient_with_invalid_email(client: TestClient) -> None:
    data = {
        'name': 'John Doe',
        'email': 'johndoe',
        'password': 'ilovepotatos',
    }

    response = client.post('/api/pacientes', json=data)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_patient_password_is_hashed(client: TestClient, patient: UserSchema) -> None:
    with DatabaseConnectionHandler() as db:
        user_data = db.session.scalar(select(User).where(User.email == patient.email))

    assert user_data is not None
    assert user_data.password != patient.password
    assert patient.verify_password(user_data.password)


def test_get_all_patients(client: TestClient, patient: UserSchema, another_patient: UserSchema) -> None:
    PATIENTS_COUNT = 2

    response = client.get('/api/pacientes')
    response_data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(response_data) == PATIENTS_COUNT
    assert response_data[0]['name'] == patient.name
    assert response_data[0]['email'] == patient.email
    assert response_data[0]['role'] == 'PATIENT'
    assert response_data[1]['name'] == another_patient.name
    assert response_data[1]['email'] == another_patient.email
    assert response_data[1]['role'] == Roles.PATIENT
    assert 'password' not in response_data[0]
    assert 'password' not in response_data[1]
    assert 'created_at' in response_data[0]
    assert 'created_at' in response_data[1]
    assert 'id' in response_data[0]
    assert 'id' in response_data[1]


def test_get_all_patients_with_no_patients(client: TestClient) -> None:
    response = client.get('/api/pacientes')
    response_data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(response_data) == 0


def test_get_patient_by_id(client: TestClient, patient: UserSchema) -> None:
    response = client.get(f'/api/pacientes/{patient.id}')
    response_data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert response_data['name'] == patient.name
    assert response_data['email'] == patient.email
    assert response_data['role'] == Roles.PATIENT
    assert 'password' not in response_data
    assert 'created_at' in response_data
    assert 'id' in response_data
    assert response_data['id'] == str(patient.id)


def test_get_patient_by_id_with_invalid_id(client: TestClient) -> None:
    response = client.get(f'/api/pacientes/{uuid4()}')
    response_data = response.json()

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response_data['detail'] == 'Usuário não encontrado'


def test_update_patient_success(client: TestClient, patient: UserSchema, token: str) -> None:
    update_data = {
        'name': 'John Updated',
        'email': 'john.updated@example.com',
        'password': 'newpassword',
        'role': Roles.PATIENT,
    }
    response = client.put(
        f'/api/pacientes/{patient.id}', headers={'Authorization': f'Bearer {token}'}, json=update_data
    )
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert data['id'] == str(patient.id)
    assert data['name'] == 'John Updated'
    assert data['email'] == 'john.updated@example.com'


def test_update_patient_cannot_change_role(client: TestClient, patient: UserSchema, token: str) -> None:
    update_data = {'name': 'John Doe', 'email': 'johndoe@example.com', 'password': 'ilovepotatos', 'role': Roles.ADMIN}
    response = client.put(
        f'/api/pacientes/{patient.id}', headers={'Authorization': f'Bearer {token}'}, json=update_data
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_delete_patient_success(client: TestClient, another_patient: UserSchema, admin_token: str) -> None:
    response = client.delete(f'/api/pacientes/{another_patient.id}', headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == HTTPStatus.NO_CONTENT

    get_response = client.get(f'/api/pacientes/{another_patient.id}')
    assert get_response.status_code == HTTPStatus.NOT_FOUND


def test_delete_patient_unauthorized(client: TestClient, patient: UserSchema, token: str) -> None:
    response = client.delete(f'/api/pacientes/{patient.id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code in {HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN}


def test_delete_patient_not_found(client: TestClient, admin_token: str) -> None:
    response = client.delete(
        '/api/pacientes/00000000-0000-0000-0000-000000000000', headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND

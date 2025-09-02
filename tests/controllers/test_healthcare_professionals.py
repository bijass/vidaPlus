from http import HTTPStatus
from uuid import uuid4

from fastapi.testclient import TestClient

from vidaplus.main.enums.roles import Roles
from vidaplus.main.schemas.appointment import AppointmentSchema
from vidaplus.main.schemas.user import UserSchema


def test_create_healthcare_professional(client: TestClient, admin: UserSchema, admin_token: str) -> None:
    data = {
        'name': 'Jane Doe',
        'email': 'janedoe@example.com',
        'password': 'ilovestrawberries',
    }

    response = client.post('/api/profissionais', json=data, headers={'Authorization': f'Bearer {admin_token}'})
    response_data = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert response_data['name'] == data['name']
    assert response_data['email'] == data['email']
    assert response_data['role'] == Roles.HEALTHCARE_PROFESSIONAL
    assert 'id' in response_data
    assert 'created_at' in response_data
    assert 'password' not in response_data


def test_create_healthcare_professional_without_token(client: TestClient) -> None:
    data = {
        'name': 'Jane Doe',
        'email': 'janedoe@example.com',
        'password': 'ilovestrawberries',
    }

    response = client.post('/api/profissionais', json=data)
    response_data = response.json()

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response_data['detail'] == 'Not authenticated'


def test_create_healthcare_professional_another_role(client: TestClient, token: str) -> None:
    data = {
        'name': 'Jane Doe',
        'email': 'janedoe@example.com',
        'password': 'ilovestrawberries',
    }

    response = client.post('/api/profissionais', json=data, headers={'Authorization': f'Bearer {token}'})
    response_data = response.json()

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response_data['detail'] == 'Você não tem permissão para acessar este recurso'


def test_get_healthcare_professionals(
    client: TestClient,
    healthcare_professional: UserSchema,
    another_healthcare_professional: UserSchema,
    admin_token: str,
) -> None:
    HEALTHCARE_PROFESSIONALS_COUNT = 2

    response = client.get('/api/profissionais', headers={'Authorization': f'Bearer {admin_token}'})
    response_data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(response_data) == HEALTHCARE_PROFESSIONALS_COUNT
    assert response_data[0]['name'] == healthcare_professional.name
    assert response_data[0]['email'] == healthcare_professional.email
    assert response_data[0]['role'] == healthcare_professional.role
    assert response_data[0]['id'] == str(healthcare_professional.id)
    assert response_data[0]['created_at'] == healthcare_professional.created_at.isoformat()
    assert 'password' not in response_data[0]
    assert response_data[1]['name'] == another_healthcare_professional.name
    assert response_data[1]['email'] == another_healthcare_professional.email
    assert response_data[1]['role'] == another_healthcare_professional.role
    assert response_data[1]['id'] == str(another_healthcare_professional.id)
    assert response_data[1]['created_at'] == another_healthcare_professional.created_at.isoformat()
    assert 'password' not in response_data[1]


def test_get_healthcare_professsional_by_id(
    client: TestClient, healthcare_professional: UserSchema, admin_token: str
) -> None:
    response = client.get(
        f'/api/profissionais/{healthcare_professional.id}', headers={'Authorization': f'Bearer {admin_token}'}
    )
    response_data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert response_data['name'] == healthcare_professional.name
    assert response_data['email'] == healthcare_professional.email
    assert response_data['role'] == healthcare_professional.role
    assert response_data['id'] == str(healthcare_professional.id)
    assert response_data['created_at'] == healthcare_professional.created_at.isoformat()
    assert 'password' not in response_data


def test_get_healthcare_professional_without_admin_token(
    client: TestClient, healthcare_professional: UserSchema, token: str
) -> None:
    response = client.get(
        f'/api/profissionais/{healthcare_professional.id}', headers={'Authorization': f'Bearer {token}'}
    )
    response_data = response.json()

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response_data['detail'] == 'Você não tem permissão para acessar este recurso'


def test_get_healthcare_professional_by_id_not_found(client: TestClient, admin_token: str) -> None:
    response = client.get(f'/api/profissionais/{uuid4()}', headers={'Authorization': f'Bearer {admin_token}'})
    response_data = response.json()

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response_data['detail'] == 'Usuário não encontrado'


def test_list_healthcare_professional_appointments(
    client: TestClient,
    healthcare_professional: UserSchema,
    appointment: AppointmentSchema,
    healthcare_professional_token: str,
) -> None:
    response = client.get(
        f'/api/profissionais/{healthcare_professional.id}/agendamentos',
        headers={'Authorization': f'Bearer {healthcare_professional_token}'},
    )
    response_data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(response_data) == 1

    appt = response_data[0]

    assert appt['id'] == appointment.id
    assert appt['date_time'] == appointment.date_time.isoformat()
    assert appt['status'] == appointment.status
    assert appt['patient_id'] == str(appointment.patient_id)
    assert appt['professional_id'] == str(appointment.professional_id)
    assert appt['created_at'] == appointment.created_at.isoformat()
    assert appt['updated_at'] == appointment.updated_at.isoformat()


def test_update_professional_success(
    client: TestClient, healthcare_professional: UserSchema, healthcare_professional_token: str
) -> None:
    update_data = {
        'name': 'Dr. Updated',
        'email': 'dr.updated@example.com',
        'password': 'newstrongpass',
        'role': Roles.HEALTHCARE_PROFESSIONAL,
    }
    response = client.put(
        f'/api/profissionais/{healthcare_professional.id}',
        headers={'Authorization': f'Bearer {healthcare_professional_token}'},
        json=update_data,
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['id'] == str(healthcare_professional.id)
    assert data['name'] == 'Dr. Updated'
    assert data['email'] == 'dr.updated@example.com'


def test_update_professional_cannot_change_role(
    client: TestClient, healthcare_professional: UserSchema, healthcare_professional_token: str
) -> None:
    update_data = {'name': 'Dr. Locked', 'email': 'locked@example.com', 'password': 'pw', 'role': Roles.ADMIN}
    response = client.put(
        f'/api/profissionais/{healthcare_professional.id}',
        headers={'Authorization': f'Bearer {healthcare_professional_token}'},
        json=update_data,
    )
    assert response.status_code in {HTTPStatus.UNPROCESSABLE_ENTITY, HTTPStatus.FORBIDDEN}


def test_update_professional_unauthorized(client: TestClient, healthcare_professional: UserSchema) -> None:
    update_data = {'name': 'Unauthorized', 'email': 'unauth@example.com', 'password': 'pw'}
    response = client.put(f'/api/profissionais/{healthcare_professional.id}', json=update_data)
    assert response.status_code in {HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN}


def test_update_professional_not_found(client: TestClient, healthcare_professional_token: str) -> None:
    update_data = {
        'name': 'No One',
        'email': 'noone@example.com',
        'password': 'pw',
        'role': Roles.HEALTHCARE_PROFESSIONAL,
    }
    fake_id = '00000000-0000-0000-0000-000000000000'
    response = client.put(
        f'/api/profissionais/{fake_id}',
        headers={'Authorization': f'Bearer {healthcare_professional_token}'},
        json=update_data,
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_professional_success(
    client: TestClient, another_healthcare_professional: UserSchema, admin_token: str
) -> None:
    response = client.delete(
        f'/api/profissionais/{another_healthcare_professional.id}', headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == HTTPStatus.NO_CONTENT

    get_response = client.get(
        f'/api/profissionais/{another_healthcare_professional.id}', headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert get_response.status_code == HTTPStatus.NOT_FOUND


def test_delete_professional_unauthorized(
    client: TestClient, healthcare_professional: UserSchema, healthcare_professional_token: str
) -> None:
    response = client.delete(
        f'/api/profissionais/{healthcare_professional.id}',
        headers={'Authorization': f'Bearer {healthcare_professional_token}'},
    )
    assert response.status_code in {HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN}


def test_delete_professional_not_found(client: TestClient, admin_token: str) -> None:
    fake_id = '00000000-0000-0000-0000-000000000000'
    response = client.delete(f'/api/profissionais/{fake_id}', headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND

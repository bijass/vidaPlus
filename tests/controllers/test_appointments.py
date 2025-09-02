import random
from datetime import datetime, timedelta
from http import HTTPStatus

from fastapi.testclient import TestClient

from vidaplus.main.enums.appointment_status import AppointmentStatus
from vidaplus.main.enums.appointment_types import AppointmentTypes
from vidaplus.main.schemas.appointment import AppointmentSchema
from vidaplus.main.schemas.user import UserSchema


def test_create_appointment(
    client: TestClient, patient: UserSchema, healthcare_professional: UserSchema, token: str, date_in_future: str
) -> None:
    data = {
        'patient_id': str(patient.id),
        'professional_id': str(healthcare_professional.id),
        'date_time': date_in_future,
        'type': AppointmentTypes.CONSULTATION,
        'status': AppointmentStatus.SCHEDULED,
        'estimated_duration': random.randint(1, 60),
        'location': 'Endereço ou link de telemedicina',
        'notes': 'Notas sobre o paciente',
    }

    response = client.post('/api/agendamentos', json=data, headers={'Authorization': f'Bearer {token}'})
    response_data = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert response_data['patient_id'] == data['patient_id']
    assert response_data['date_time'] == data['date_time']
    assert response_data['type'] == data['type']
    assert response_data['status'] == data['status']
    assert response_data['estimated_duration'] == data['estimated_duration']
    assert response_data['location'] == data['location']
    assert response_data['notes'] == data['notes']
    assert 'id' in response_data
    assert 'created_at' in response_data
    assert 'updated_at' in response_data


def test_create_appointment_without_authorization(client: TestClient, date_in_future: str) -> None:
    data = {
        'patient_id': '123',
        'professional_id': '456',
        'date_time': date_in_future,
        'type': AppointmentTypes.CONSULTATION,
        'status': AppointmentStatus.SCHEDULED,
        'estimated_duration': random.randint(1, 60),
        'location': 'Endereço ou link de telemedicina',
        'notes': 'Notas sobre o paciente',
    }

    response = client.post('/api/agendamentos', json=data)
    response_data = response.json()

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response_data['detail'] == 'Not authenticated'


def test_create_appointment_with_invalid_patient_id(
    client: TestClient, healthcare_professional: UserSchema, token: str, date_in_future: str
) -> None:
    data = {
        'patient_id': 'invalid-uuid-123',
        'professional_id': str(healthcare_professional.id),
        'date_time': date_in_future,
        'type': AppointmentTypes.CONSULTATION,
        'status': AppointmentStatus.SCHEDULED,
        'estimated_duration': 30,
        'location': 'Sala 205',
        'notes': 'Paciente inexistente',
    }

    response = client.post('/api/agendamentos', json=data, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert 'patient_id' in response.text


def test_create_appointment_with_past_date(
    client: TestClient, patient: UserSchema, healthcare_professional: UserSchema, token: str
) -> None:
    date_in_past = datetime.now() - timedelta(days=random.randint(1, 30))

    data = {
        'patient_id': str(patient.id),
        'professional_id': str(healthcare_professional.id),
        'date_time': date_in_past.isoformat(),
        'type': AppointmentTypes.CONSULTATION,
        'status': AppointmentStatus.SCHEDULED,
        'estimated_duration': 30,
        'location': 'Sala 205',
        'notes': 'Data inválida',
    }

    response = client.post('/api/agendamentos', json=data, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Não é possível agendar no passado' in response.json()['detail']


def test_create_conflicting_appointment(
    client: TestClient, patient: UserSchema, healthcare_professional: UserSchema, token: str, date_in_future: str
) -> None:
    base_data = {
        'patient_id': str(patient.id),
        'professional_id': str(healthcare_professional.id),
        'date_time': date_in_future,
        'type': AppointmentTypes.CONSULTATION,
        'status': AppointmentStatus.SCHEDULED,
        'estimated_duration': 60,
        'location': 'Sala 205',
        'notes': 'Conflito',
    }

    response1 = client.post('/api/agendamentos', json=base_data, headers={'Authorization': f'Bearer {token}'})
    assert response1.status_code == HTTPStatus.CREATED

    response2 = client.post('/api/agendamentos', json=base_data, headers={'Authorization': f'Bearer {token}'})
    assert response2.status_code == HTTPStatus.CONFLICT
    assert 'Já existe um agendamento no mesmo horário' in response2.json()['detail']


def test_create_appointment_with_missing_fields(client: TestClient, token: str) -> None:
    incomplete_data = {'date_time': datetime.now().isoformat(), 'type': AppointmentTypes.CONSULTATION}

    response = client.post('/api/agendamentos', json=incomplete_data, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert 'patient_id' in response.text
    assert 'location' in response.text


def test_patient_creating_appointment_for_another_patient(
    client: TestClient,
    another_patient: UserSchema,
    healthcare_professional: UserSchema,
    token: str,
    date_in_future: str,
) -> None:
    data = {
        'patient_id': str(another_patient.id),
        'professional_id': str(healthcare_professional.id),
        'date_time': date_in_future,
        'type': AppointmentTypes.CONSULTATION,
        'status': AppointmentStatus.SCHEDULED,
        'estimated_duration': 30,
        'location': 'Sala 205',
        'notes': 'Acesso não autorizado',
    }

    response = client.post('/api/agendamentos', json=data, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert 'Você não tem permissão para acessar este recurso' in response.json()['detail']


def test_healthcare_professional_creating_appointment_for_a_patient(
    client: TestClient,
    patient: UserSchema,
    healthcare_professional: UserSchema,
    token: str,
    date_in_future: str,
) -> None:
    APPOINTMENT_DURATION_IN_MINUTES = 30
    data = {
        'patient_id': str(patient.id),
        'professional_id': str(healthcare_professional.id),
        'date_time': date_in_future,
        'type': AppointmentTypes.CONSULTATION,
        'status': AppointmentStatus.SCHEDULED,
        'estimated_duration': APPOINTMENT_DURATION_IN_MINUTES,
        'location': 'Sala 205',
        'notes': 'Agendamento criado pelo profissional',
    }

    response = client.post('/api/agendamentos', json=data, headers={'Authorization': f'Bearer {token}'})
    response_data = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert response_data['patient_id'] == str(patient.id)
    assert response_data['professional_id'] == str(healthcare_professional.id)
    assert response_data['type'] == AppointmentTypes.CONSULTATION
    assert response_data['status'] == AppointmentStatus.SCHEDULED
    assert response_data['estimated_duration'] == APPOINTMENT_DURATION_IN_MINUTES
    assert response_data['location'] == 'Sala 205'
    assert response_data['notes'] == 'Agendamento criado pelo profissional'


def test_admin_creating_appointment_for_a_patient(
    client: TestClient,
    patient: UserSchema,
    healthcare_professional: UserSchema,
    admin_token: str,
    date_in_future: str,
) -> None:
    APPOINTMENT_DURATION_IN_MINUTES = 30
    data = {
        'patient_id': str(patient.id),
        'professional_id': str(healthcare_professional.id),
        'date_time': date_in_future,
        'type': AppointmentTypes.CONSULTATION,
        'status': AppointmentStatus.SCHEDULED,
        'estimated_duration': APPOINTMENT_DURATION_IN_MINUTES,
        'location': 'Sala 205',
        'notes': 'Agendamento criado pelo administrador',
    }

    response = client.post('/api/agendamentos', json=data, headers={'Authorization': f'Bearer {admin_token}'})
    response_data = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert response_data['patient_id'] == str(patient.id)
    assert response_data['professional_id'] == str(healthcare_professional.id)
    assert response_data['type'] == AppointmentTypes.CONSULTATION
    assert response_data['status'] == AppointmentStatus.SCHEDULED
    assert response_data['estimated_duration'] == APPOINTMENT_DURATION_IN_MINUTES
    assert response_data['location'] == 'Sala 205'
    assert response_data['notes'] == 'Agendamento criado pelo administrador'


def test_list_appointments_with_filters(
    client: TestClient, patient: UserSchema, healthcare_professional: UserSchema, token: str
) -> None:
    APPOINTMENTS_COUNT = 3

    for i in range(APPOINTMENTS_COUNT):
        client.post(
            '/api/agendamentos',
            json={
                'patient_id': str(patient.id),
                'professional_id': str(healthcare_professional.id),
                'date_time': (datetime.now() + timedelta(days=i + 1)).isoformat(),
                'type': AppointmentTypes.CONSULTATION,
                'status': AppointmentStatus.SCHEDULED,
                'estimated_duration': 30,
                'location': 'Sala 205',
                'notes': f'Consulta {i}',
            },
            headers={'Authorization': f'Bearer {token}'},
        )

    # Lista todos os agendamentos
    response = client.get('/api/agendamentos', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == APPOINTMENTS_COUNT


def test_filter_by_patient_id(
    client: TestClient, patient: UserSchema, healthcare_professional: UserSchema, token: str
) -> None:
    APPOINTMENT_COUNT = 2

    for i in range(APPOINTMENT_COUNT):
        client.post(
            '/api/agendamentos',
            json={
                'patient_id': str(patient.id),
                'professional_id': str(healthcare_professional.id),
                'date_time': (datetime.now() + timedelta(days=i + 1)).isoformat(),
                'type': AppointmentTypes.CONSULTATION,
                'status': AppointmentStatus.SCHEDULED,
                'estimated_duration': 30,
                'location': 'Sala 205',
                'notes': f'Consulta {i}',
            },
            headers={'Authorization': f'Bearer {token}'},
        )

    # Filtra por patient_id
    response = client.get(f'/api/agendamentos?patient_id={patient.id}', headers={'Authorization': f'Bearer {token}'})
    appointments = response.json()
    assert len(appointments) == APPOINTMENT_COUNT
    assert all(appt['patient_id'] == str(patient.id) for appt in appointments)


def test_filter_by_date_range(
    client: TestClient, patient: UserSchema, healthcare_professional: UserSchema, token: str
) -> None:
    APPOINTMENT_COUNT = 1

    dates = [
        (datetime.now() + timedelta(days=2)).isoformat(),  # Dentro do range
        (datetime.now() + timedelta(days=5)).isoformat(),  # Fora do range
    ]
    for date in dates:
        client.post(
            '/api/agendamentos',
            json={
                'patient_id': str(patient.id),
                'professional_id': str(healthcare_professional.id),
                'date_time': date,
                'type': AppointmentTypes.CONSULTATION,
                'status': AppointmentStatus.SCHEDULED,
                'estimated_duration': 30,
                'location': 'Sala 205',
                'notes': 'Consulta',
            },
            headers={'Authorization': f'Bearer {token}'},
        )

    # Filtra por intervalo de datas
    start_date = (datetime.now() + timedelta(days=1)).isoformat()
    end_date = (datetime.now() + timedelta(days=3)).isoformat()
    response = client.get(
        f'/api/agendamentos?start_date={start_date}&end_date={end_date}', headers={'Authorization': f'Bearer {token}'}
    )
    assert len(response.json()) == APPOINTMENT_COUNT


def test_invalid_date_filter(client: TestClient, token: str) -> None:
    # Data inválida
    response = client.get('/api/agendamentos?start_date=2023-13-01', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_empty_response(client: TestClient, token: str) -> None:
    APPOINTMENT_COUNT = 0

    response = client.get(
        '/api/agendamentos?patient_id=00000000-0000-0000-0000-000000000000',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == APPOINTMENT_COUNT


def test_patient_cannot_list_all_appointments(
    client: TestClient,
    patient: UserSchema,
    another_patient: UserSchema,
    healthcare_professional: UserSchema,
    token: str,
) -> None:
    APPOINTMENT_COUNT = 0

    client.post(
        '/api/agendamentos',
        json={
            'patient_id': str(another_patient.id),
            'professional_id': str(healthcare_professional.id),
            'date_time': (datetime.now() + timedelta(days=1)).isoformat(),
            'type': AppointmentTypes.CONSULTATION,
            'status': AppointmentStatus.SCHEDULED,
            'estimated_duration': 30,
            'location': 'Sala 205',
            'notes': 'Consulta privada',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    response = client.get('/api/agendamentos', headers={'Authorization': f'Bearer {token}'})
    assert len(response.json()) == APPOINTMENT_COUNT


def test_cancel_appointment(
    client: TestClient, patient: UserSchema, appointment: AppointmentSchema, token: str
) -> None:
    response = client.delete(f'/api/agendamentos/{appointment.id}', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_cancel_appointment_not_found(client: TestClient, patient: UserSchema, token: str) -> None:
    response = client.delete('/api/agendamentos/100000000', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Agendamento não encontrado'}


def test_cancel_appointment_unauthorized(
    client: TestClient, patient: UserSchema, appointment: AppointmentSchema
) -> None:
    response = client.delete(f'/api/agendamentos/{appointment.id}')

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_update_appointment(
    client: TestClient, patient: UserSchema, appointment: AppointmentSchema, token: str
) -> None:
    updated_data = {
        'patient_id': str(patient.id),
        'professional_id': str(appointment.professional_id),
        'date_time': (datetime.now() + timedelta(days=1)).isoformat(),
        'type': AppointmentTypes.CONSULTATION,
        'status': AppointmentStatus.SCHEDULED,
        'estimated_duration': 30,
        'location': 'Sala 205',
        'notes': 'Consulta privada',
    }

    response = client.put(
        f'/api/agendamentos/{appointment.id}',
        json=updated_data,
        headers={'Authorization': f'Bearer {token}'},
    )
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert data['id'] == appointment.id
    assert data['patient_id'] == str(patient.id)
    assert data['professional_id'] == str(appointment.professional_id)
    assert data['date_time'] == updated_data['date_time']
    assert data['type'] == updated_data['type']
    assert data['status'] == updated_data['status']
    assert data['estimated_duration'] == updated_data['estimated_duration']
    assert data['location'] == updated_data['location']
    assert data['notes'] == updated_data['notes']


def test_update_appointment_not_found(client: TestClient, patient: UserSchema, token: str) -> None:
    updated_data = {
        'patient_id': str(patient.id),
        'professional_id': str(patient.id),
        'date_time': (datetime.now() + timedelta(days=1)).isoformat(),
        'type': AppointmentTypes.CONSULTATION,
        'status': AppointmentStatus.SCHEDULED,
        'estimated_duration': 30,
        'location': 'Sala 205',
        'notes': 'Consulta privada',
    }

    response = client.put(
        '/api/agendamentos/100000000',
        json=updated_data,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Agendamento não encontrado'}


def test_update_appointment_unauthorized(
    client: TestClient, patient: UserSchema, appointment: AppointmentSchema
) -> None:
    updated_data = {
        'patient_id': str(patient.id),
        'professional_id': str(patient.id),
        'date_time': (datetime.now() + timedelta(days=1)).isoformat(),
        'type': AppointmentTypes.CONSULTATION,
        'status': AppointmentStatus.SCHEDULED,
        'estimated_duration': 30,
        'location': 'Sala 205',
        'notes': 'Consulta privada',
    }

    response = client.put(f'/api/agendamentos/{appointment.id}', json=updated_data)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}

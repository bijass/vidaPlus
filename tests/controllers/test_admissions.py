from datetime import datetime, timedelta
from http import HTTPStatus

from fastapi.testclient import TestClient

from vidaplus.main.enums.bed_status import BedStatus
from vidaplus.main.schemas.bed import BedSchema
from vidaplus.main.schemas.user import UserSchema
from vidaplus.models.config.connection import DatabaseConnectionHandler
from vidaplus.models.entities.bed import Bed


def test_list_admissions_empty(client: TestClient) -> None:
    response = client.get('/api/internacoes/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


def test_create_admission_forbidden_for_non_admin(
    client: TestClient, token: str, patient: UserSchema, bed: BedSchema
) -> None:
    payload = {'patient_id': str(patient.id), 'bed_id': bed.id}
    response = client.post('/api/internacoes/', headers={'Authorization': f'Bearer {token}'}, json=payload)
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_create_admission_not_found_resources(
    client: TestClient, admin_token: str, patient: UserSchema, bed: BedSchema
) -> None:
    payload = {'patient_id': '00000000-0000-0000-0000-000000000000', 'bed_id': bed.id}
    resp1 = client.post('/api/internacoes/', headers={'Authorization': f'Bearer {admin_token}'}, json=payload)
    assert resp1.status_code == HTTPStatus.NOT_FOUND

    payload = {'patient_id': str(patient.id), 'bed_id': 9999}
    resp2 = client.post('/api/internacoes/', headers={'Authorization': f'Bearer {admin_token}'}, json=payload)
    assert resp2.status_code == HTTPStatus.NOT_FOUND


def test_create_admission_success(client: TestClient, admin_token: str, patient: UserSchema, bed: BedSchema) -> None:
    payload = {'patient_id': str(patient.id), 'bed_id': bed.id}
    resp = client.post('/api/internacoes/', headers={'Authorization': f'Bearer {admin_token}'}, json=payload)
    data = resp.json()

    assert resp.status_code == HTTPStatus.CREATED
    assert isinstance(data['id'], int)
    assert data['patient_id'] == str(patient.id)
    assert data['bed_id'] == bed.id
    assert 'admitted_at' in data


def test_create_admission_bed_unavailable(
    client: TestClient, admin_token: str, patient: UserSchema, bed: BedSchema
) -> None:
    with DatabaseConnectionHandler() as db:
        bed_obj = db.session.get(Bed, bed.id)

        if bed_obj:
            bed_obj.status = BedStatus.OCCUPIED

        db.session.commit()

    payload = {'patient_id': str(patient.id), 'bed_id': bed.id}
    response = client.post('/api/internacoes/', headers={'Authorization': f'Bearer {admin_token}'}, json=payload)
    assert response.status_code == HTTPStatus.CONFLICT


def test_list_admissions_with_data(client: TestClient, admin_token: str, patient: UserSchema, bed: BedSchema) -> None:
    payload = {'patient_id': str(patient.id), 'bed_id': bed.id}
    adm = client.post('/api/internacoes/', headers={'Authorization': f'Bearer {admin_token}'}, json=payload).json()
    response = client.get('/api/internacoes/')
    assert response.status_code == HTTPStatus.OK
    ids = {a['id'] for a in response.json()}
    assert adm['id'] in ids


def test_get_admission_success(client: TestClient, admin_token: str, patient: UserSchema, bed: BedSchema) -> None:
    payload = {'patient_id': str(patient.id), 'bed_id': bed.id}
    adm = client.post('/api/internacoes/', headers={'Authorization': f'Bearer {admin_token}'}, json=payload).json()
    resp = client.get(f'/api/internacoes/{adm["id"]}')
    data = resp.json()

    assert resp.status_code == HTTPStatus.OK
    assert data['id'] == adm['id']
    assert data['patient_id'] == str(patient.id)


def test_get_admission_not_found(client: TestClient) -> None:
    resp = client.get('/api/internacoes/9999')
    assert resp.status_code == HTTPStatus.NOT_FOUND


def test_update_admission_forbidden_for_non_admin(
    client: TestClient, token: str, admin_token: str, patient: UserSchema, bed: BedSchema
) -> None:
    adm = client.post(
        '/api/internacoes/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'patient_id': str(patient.id), 'bed_id': bed.id},
    ).json()
    update = {'bed_id': bed.id, 'discharged_at': (datetime.now() + timedelta(days=1)).isoformat()}
    resp = client.put(f'/api/internacoes/{adm["id"]}', headers={'Authorization': f'Bearer {token}'}, json=update)
    assert resp.status_code == HTTPStatus.FORBIDDEN


def test_update_admission_not_found(client: TestClient, admin_token: str) -> None:
    update = {'bed_id': 1, 'discharged_at': (datetime.now() + timedelta(days=1)).isoformat()}
    resp = client.put('/api/internacoes/9999', headers={'Authorization': f'Bearer {admin_token}'}, json=update)
    assert resp.status_code == HTTPStatus.NOT_FOUND


def test_update_admission_success(client: TestClient, admin_token: str, patient: UserSchema, bed: BedSchema) -> None:
    adm = client.post(
        '/api/internacoes/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'patient_id': str(patient.id), 'bed_id': bed.id},
    ).json()
    new_bed = Bed(unit_id=bed.unit_id, type='ICU', status='AVAILABLE')
    with DatabaseConnectionHandler() as db:
        db.session.add(new_bed)
        db.session.commit()
        db.session.refresh(new_bed)
    update = {'bed_id': new_bed.id, 'discharged_at': (datetime.now() + timedelta(days=2)).isoformat()}
    resp = client.put(f'/api/internacoes/{adm["id"]}', headers={'Authorization': f'Bearer {admin_token}'}, json=update)
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data['bed_id'] == new_bed.id
    assert 'discharged_at' in data


def test_delete_admission_not_found(client: TestClient, admin_token: str) -> None:
    resp = client.delete('/api/internacoes/9999', headers={'Authorization': f'Bearer {admin_token}'})
    assert resp.status_code == HTTPStatus.NOT_FOUND


def test_delete_admission_success(client: TestClient, admin_token: str, patient: UserSchema, bed: BedSchema) -> None:
    adm = client.post(
        '/api/internacoes/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'patient_id': str(patient.id), 'bed_id': bed.id},
    ).json()
    resp = client.delete(f'/api/internacoes/{adm["id"]}', headers={'Authorization': f'Bearer {admin_token}'})
    assert resp.status_code == HTTPStatus.NO_CONTENT

    resp = client.get(f'/api/internacoes/{adm["id"]}')
    assert resp.status_code == HTTPStatus.NOT_FOUND


def test_delete_admission_forbidden_for_non_admin(
    client: TestClient, token: str, admin_token: str, patient: UserSchema, bed: BedSchema
) -> None:
    adm = client.post(
        '/api/internacoes/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'patient_id': str(patient.id), 'bed_id': bed.id},
    ).json()
    resp = client.delete(f'/api/internacoes/{adm["id"]}', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == HTTPStatus.FORBIDDEN

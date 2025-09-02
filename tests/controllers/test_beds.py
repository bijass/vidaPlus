from http import HTTPStatus

from fastapi.testclient import TestClient


def test_list_beds_empty(client: TestClient) -> None:
    response = client.get('/api/leitos/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


def test_create_bed_forbidden_for_non_admin(client: TestClient, token: str) -> None:
    payload = {'unit_id': 1, 'type': 'STANDARD', 'status': 'AVAILABLE'}
    response = client.post('/api/leitos/', headers={'Authorization': f'Bearer {token}'}, json=payload)
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_create_bed_unit_not_found(client: TestClient, admin_token: str) -> None:
    # Attempt to create bed for non-existent unit
    payload = {'unit_id': 9999, 'type': 'ICU', 'status': 'AVAILABLE'}
    response = client.post('/api/leitos/', headers={'Authorization': f'Bearer {admin_token}'}, json=payload)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_create_bed_success(client: TestClient, admin_token: str) -> None:
    unit_resp = client.post(
        '/api/unidades/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'name': 'Unidade Teste', 'address': 'Rua Teste, 1'},
    )
    unit_id = unit_resp.json()['id']

    payload = {'unit_id': unit_id, 'type': 'ICU', 'status': 'AVAILABLE'}
    response = client.post('/api/leitos/', headers={'Authorization': f'Bearer {admin_token}'}, json=payload)
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert isinstance(data['id'], int)
    assert data['unit_id'] == unit_id
    assert data['type'] == 'ICU'
    assert data['status'] == 'AVAILABLE'


def test_list_beds_with_data(client: TestClient, admin_token: str) -> None:
    unit_resp = client.post(
        '/api/unidades/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'name': 'Unidade A', 'address': 'Addr A'},
    )
    unit_id = unit_resp.json()['id']

    bed_ids = []
    for typ, stat in [('STANDARD', 'AVAILABLE'), ('ICU', 'OCCUPIED')]:
        bed_ids.append(
            client.post(
                '/api/leitos/',
                headers={'Authorization': f'Bearer {admin_token}'},
                json={'unit_id': unit_id, 'type': typ, 'status': stat},
            ).json()['id']
        )

    list_resp = client.get('/api/leitos/')
    assert list_resp.status_code == HTTPStatus.OK
    beds = list_resp.json()
    ids = {b['id'] for b in beds}
    assert set(bed_ids).issubset(ids)
    # Check relation: all beds refer to the same unit
    assert all(b['unit_id'] == unit_id for b in beds if b['id'] in bed_ids)


def test_get_bed_success(client: TestClient, admin_token: str) -> None:
    # Setup: create unit and bed
    unit_id = client.post(
        '/api/unidades/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'name': 'Unidade Y', 'address': 'Addr Y'},
    ).json()['id']
    bed_id = client.post(
        '/api/leitos/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'unit_id': unit_id, 'type': 'STANDARD', 'status': 'AVAILABLE'},
    ).json()['id']

    response = client.get(f'/api/leitos/{bed_id}')
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['id'] == bed_id
    assert data['unit_id'] == unit_id
    assert data['type'] == 'STANDARD'
    assert data['status'] == 'AVAILABLE'


def test_get_bed_not_found(client: TestClient) -> None:
    response = client.get('/api/leitos/9999')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_bed_forbidden_for_non_admin(client: TestClient, token: str, admin_token: str) -> None:
    unit_id = client.post(
        '/api/unidades/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'name': 'Unidade B', 'address': 'Addr B'},
    ).json()['id']
    bed_id = client.post(
        '/api/leitos/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'unit_id': unit_id, 'type': 'STANDARD', 'status': 'AVAILABLE'},
    ).json()['id']

    update = {'unit_id': unit_id, 'type': 'ICU', 'status': 'OCCUPIED'}
    response = client.put(f'/api/leitos/{bed_id}', headers={'Authorization': f'Bearer {token}'}, json=update)
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_update_bed_not_found(client: TestClient, admin_token: str) -> None:
    response = client.put(
        '/api/leitos/9999',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'unit_id': -1, 'type': 'ICU', 'status': 'AVAILABLE'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_bed_success(client: TestClient, admin_token: str) -> None:
    unit_id = client.post(
        '/api/unidades/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'name': 'Unidade C', 'address': 'Addr C'},
    ).json()['id']
    bed_id = client.post(
        '/api/leitos/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'unit_id': unit_id, 'type': 'STANDARD', 'status': 'AVAILABLE'},
    ).json()['id']

    update = {'unit_id': unit_id, 'type': 'ICU', 'status': 'OCCUPIED'}
    response = client.put(f'/api/leitos/{bed_id}', headers={'Authorization': f'Bearer {admin_token}'}, json=update)
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert data['id'] == bed_id
    assert data['unit_id'] == unit_id
    assert data['type'] == 'ICU'
    assert data['status'] == 'OCCUPIED'


def test_delete_bed_forbidden_for_non_admin(client: TestClient, token: str, admin_token: str) -> None:
    unit_id = client.post(
        '/api/unidades/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'name': 'Unidade D', 'address': 'Addr D'},
    ).json()['id']
    bed_id = client.post(
        '/api/leitos/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'unit_id': unit_id, 'type': 'STANDARD', 'status': 'AVAILABLE'},
    ).json()['id']

    response = client.delete(f'/api/leitos/{bed_id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_delete_bed_not_found(client: TestClient, admin_token: str) -> None:
    response = client.delete('/api/leitos/9999', headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_bed_success(client: TestClient, admin_token: str) -> None:
    unit_id = client.post(
        '/api/unidades/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'name': 'Unidade E', 'address': 'Addr E'},
    ).json()['id']
    bed_id = client.post(
        '/api/leitos/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'unit_id': unit_id, 'type': 'ICU', 'status': 'AVAILABLE'},
    ).json()['id']

    response = client.delete(f'/api/leitos/{bed_id}', headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == HTTPStatus.NO_CONTENT
    get_resp = client.get(f'/api/leitos/{bed_id}')
    assert get_resp.status_code == HTTPStatus.NOT_FOUND

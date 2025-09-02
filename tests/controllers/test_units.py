from http import HTTPStatus

from fastapi.testclient import TestClient


def test_list_units_empty(client: TestClient) -> None:
    response = client.get('/api/unidades/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


def test_create_unit_unauthorized(client: TestClient) -> None:
    payload = {'name': 'Unidade X', 'address': 'Rua X, 1'}
    response = client.post('/api/unidades/', json=payload)
    assert response.status_code in {HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN}


def test_create_unit_forbidden_for_non_admin(client: TestClient, token: str) -> None:
    # Authenticated but not admin cannot create
    payload = {'name': 'Unidade Y', 'address': 'Rua Y, 2'}
    response = client.post('/api/unidades/', headers={'Authorization': f'Bearer {token}'}, json=payload)
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_create_unit_success(client: TestClient, admin_token: str) -> None:
    payload = {'name': 'Unidade X', 'address': 'Rua X, 1'}
    response = client.post('/api/unidades/', headers={'Authorization': f'Bearer {admin_token}'}, json=payload)
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert isinstance(data['id'], int)
    assert data['name'] == payload['name']
    assert data['address'] == payload['address']


def test_list_units_with_data(client: TestClient, admin_token: str) -> None:
    payload1 = {'name': 'Unidade A', 'address': 'Rua A, 1'}
    payload2 = {'name': 'Unidade B', 'address': 'Rua B, 2'}
    id1 = client.post('/api/unidades/', headers={'Authorization': f'Bearer {admin_token}'}, json=payload1).json()['id']
    id2 = client.post('/api/unidades/', headers={'Authorization': f'Bearer {admin_token}'}, json=payload2).json()['id']
    response = client.get('/api/unidades/')
    assert response.status_code == HTTPStatus.OK
    ids = {u['id'] for u in response.json()}
    assert id1 in ids
    assert id2 in ids


def test_get_unit_success(client: TestClient, admin_token: str) -> None:
    payload = {'name': 'Unidade Y', 'address': 'Rua Y, 9'}
    unit_id = client.post('/api/unidades/', headers={'Authorization': f'Bearer {admin_token}'}, json=payload).json()[
        'id'
    ]
    response = client.get(f'/api/unidades/{unit_id}')
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['id'] == unit_id
    assert data['name'] == payload['name']
    assert data['address'] == payload['address']


def test_get_unit_not_found(client: TestClient) -> None:
    fake_id = 9999
    response = client.get(f'/api/unidades/{fake_id}')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_unit_unauthorized(client: TestClient) -> None:
    fake_id = 9999
    payload = {'name': 'No', 'address': 'No'}
    response = client.put(f'/api/unidades/{fake_id}', json=payload)
    assert response.status_code in {HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN}


def test_update_unit_forbidden_for_non_admin(client: TestClient, token: str, admin_token: str) -> None:
    # Create a unit as admin
    payload = {'name': 'Orig', 'address': 'Rua O'}
    unit_id = client.post('/api/unidades/', headers={'Authorization': f'Bearer {admin_token}'}, json=payload).json()[
        'id'
    ]
    update = {'name': 'Updated', 'address': 'Rua U'}
    response = client.put(f'/api/unidades/{unit_id}', headers={'Authorization': f'Bearer {token}'}, json=update)
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_update_unit_not_found(client: TestClient, admin_token: str) -> None:
    fake_id = 9999
    payload = {'name': 'No', 'address': 'No'}
    response = client.put(f'/api/unidades/{fake_id}', headers={'Authorization': f'Bearer {admin_token}'}, json=payload)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_unit_success(client: TestClient, admin_token: str) -> None:
    payload = {'name': 'Orig', 'address': 'Rua O'}
    unit_id = client.post('/api/unidades/', headers={'Authorization': f'Bearer {admin_token}'}, json=payload).json()[
        'id'
    ]
    update = {'name': 'Updated', 'address': 'Rua U'}
    response = client.put(f'/api/unidades/{unit_id}', headers={'Authorization': f'Bearer {admin_token}'}, json=update)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['id'] == unit_id
    assert data['name'] == 'Updated'
    assert data['address'] == 'Rua U'


def test_delete_unit_unauthorized(client: TestClient) -> None:
    fake_id = 9999
    response = client.delete(f'/api/unidades/{fake_id}')
    assert response.status_code in {HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN}


def test_delete_unit_forbidden_for_non_admin(client: TestClient, token: str, admin_token: str) -> None:
    # Create a unit as admin
    payload = {'name': 'ToDel', 'address': 'Addr'}
    unit_id = client.post('/api/unidades/', headers={'Authorization': f'Bearer {admin_token}'}, json=payload).json()[
        'id'
    ]
    response = client.delete(f'/api/unidades/{unit_id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_delete_unit_not_found(client: TestClient, admin_token: str) -> None:
    fake_id = 9999
    response = client.delete(f'/api/unidades/{fake_id}', headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_unit_success(client: TestClient, admin_token: str) -> None:
    payload = {'name': 'ToDelete', 'address': 'Addr'}
    unit_id = client.post('/api/unidades/', headers={'Authorization': f'Bearer {admin_token}'}, json=payload).json()[
        'id'
    ]
    response = client.delete(f'/api/unidades/{unit_id}', headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == HTTPStatus.NO_CONTENT
    get_resp = client.get(f'/api/unidades/{unit_id}')
    assert get_resp.status_code == HTTPStatus.NOT_FOUND

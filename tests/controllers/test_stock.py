from http import HTTPStatus

from fastapi.testclient import TestClient


def test_list_stock_empty(client: TestClient) -> None:
    response = client.get('/api/estoque/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


def test_create_stock_forbidden_for_non_admin(client: TestClient, token: str, unit_payload: dict) -> None:
    response = client.post(
        '/api/estoque/',
        headers={'Authorization': f'Bearer {token}'},
        json={'unit_id': 1, 'name': 'Soro Fisiológico', 'quantity': 50, 'min_level': 20},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_create_stock_success(client: TestClient, admin_token: str, unit_payload: dict) -> None:
    unit_resp = client.post('/api/unidades/', headers={'Authorization': f'Bearer {admin_token}'}, json=unit_payload)
    unit = unit_resp.json()

    payload = {'unit_id': unit['id'], 'name': 'Soro Fisiológico', 'quantity': 50, 'min_level': 20}
    res = client.post('/api/estoque/', headers={'Authorization': f'Bearer {admin_token}'}, json=payload)
    data = res.json()

    assert res.status_code == HTTPStatus.CREATED
    assert isinstance(data['id'], int)
    assert data['unit_id'] == payload['unit_id']
    assert data['name'] == payload['name']
    assert data['quantity'] == payload['quantity']
    assert data['min_level'] == payload['min_level']


def test_list_stock_with_data(client: TestClient, admin_token: str, unit_payload: dict) -> None:
    unit_resp = client.post('/api/unidades/', headers={'Authorization': f'Bearer {admin_token}'}, json=unit_payload)
    unit = unit_resp.json()
    items = []
    for item in [
        {'unit_id': unit['id'], 'name': 'Gazes', 'quantity': 100, 'min_level': 50},
        {'unit_id': unit['id'], 'name': 'Luvas', 'quantity': 200, 'min_level': 100},
    ]:
        resp = client.post('/api/estoque/', headers={'Authorization': f'Bearer {admin_token}'}, json=item)
        assert resp.status_code == HTTPStatus.CREATED
        items.append(resp.json()['id'])

    list_resp = client.get('/api/estoque/')
    assert list_resp.status_code == HTTPStatus.OK
    data = list_resp.json()
    ids = {i['id'] for i in data}
    assert set(items).issubset(ids)
    # all items belong to the same unit
    assert all(i['unit_id'] == unit['id'] for i in data if i['id'] in items)


def test_update_stock_forbidden_for_non_admin(
    client: TestClient, token: str, admin_token: str, unit_payload: dict
) -> None:
    unit_resp = client.post('/api/unidades/', headers={'Authorization': f'Bearer {admin_token}'}, json=unit_payload)
    unit = unit_resp.json()
    create = client.post(
        '/api/estoque/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'unit_id': unit['id'], 'name': 'Lanterna', 'quantity': 30, 'min_level': 10},
    ).json()
    update = {'unit_id': unit['id'], 'name': 'Lanterna LED', 'quantity': 25, 'min_level': 5}
    resp = client.put(f'/api/estoque/{create["id"]}', headers={'Authorization': f'Bearer {token}'}, json=update)
    assert resp.status_code == HTTPStatus.FORBIDDEN


def test_update_stock_not_found(client: TestClient, admin_token: str, unit_payload: dict) -> None:
    # ensure unit exists
    unit_resp = client.post('/api/unidades/', headers={'Authorization': f'Bearer {admin_token}'}, json=unit_payload)
    unit = unit_resp.json()
    update = {'unit_id': unit['id'], 'name': 'X', 'quantity': 1, 'min_level': 1}
    resp = client.put('/api/estoque/9999', headers={'Authorization': f'Bearer {admin_token}'}, json=update)
    assert resp.status_code == HTTPStatus.NOT_FOUND


def test_update_stock_success(client: TestClient, admin_token: str, unit_payload: dict) -> None:
    unit_resp = client.post('/api/unidades/', headers={'Authorization': f'Bearer {admin_token}'}, json=unit_payload)
    unit = unit_resp.json()
    create = client.post(
        '/api/estoque/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'unit_id': unit['id'], 'name': 'Seringa', 'quantity': 150, 'min_level': 75},
    ).json()
    update = {'unit_id': unit['id'], 'name': 'Seringa 20ml', 'quantity': 140, 'min_level': 70}
    resp = client.put(f'/api/estoque/{create["id"]}', headers={'Authorization': f'Bearer {admin_token}'}, json=update)
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data['unit_id'] == unit['id']
    assert data['name'] == update['name']
    assert data['quantity'] == update['quantity']
    assert data['min_level'] == update['min_level']


def test_delete_stock_forbidden_for_non_admin(
    client: TestClient, token: str, admin_token: str, unit_payload: dict
) -> None:
    unit_resp = client.post('/api/unidades/', headers={'Authorization': f'Bearer {admin_token}'}, json=unit_payload)
    unit = unit_resp.json()
    create = client.post(
        '/api/estoque/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'unit_id': unit['id'], 'name': 'Escalpe', 'quantity': 20, 'min_level': 5},
    ).json()
    resp = client.delete(f'/api/estoque/{create["id"]}', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == HTTPStatus.FORBIDDEN


def test_delete_stock_not_found(client: TestClient, admin_token: str) -> None:
    resp = client.delete('/api/estoque/9999', headers={'Authorization': f'Bearer {admin_token}'})
    assert resp.status_code == HTTPStatus.NOT_FOUND


def test_delete_stock_success(client: TestClient, admin_token: str, unit_payload: dict) -> None:
    unit_resp = client.post('/api/unidades/', headers={'Authorization': f'Bearer {admin_token}'}, json=unit_payload)
    unit = unit_resp.json()
    create = client.post(
        '/api/estoque/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'unit_id': unit['id'], 'name': 'Bisturi', 'quantity': 10, 'min_level': 2},
    ).json()
    resp = client.delete(f'/api/estoque/{create["id"]}', headers={'Authorization': f'Bearer {admin_token}'})
    assert resp.status_code == HTTPStatus.NO_CONTENT

    get_resp = client.get(f'/api/estoque/{create["id"]}')
    assert get_resp.status_code == HTTPStatus.NOT_FOUND

import json
import pytest
from app import app, items_db


@pytest.fixture
def client():
    """Provide a Flask test client and clean up items_db between tests."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    items_db.clear()


class TestHealth:
    def test_health_check_returns_ok(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert data['version'] == '1.0.0'
        assert 'timestamp' in data


class TestListItems:
    def test_list_items_empty(self, client):
        response = client.get('/items')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['items'] == []

    def test_list_items_with_data(self, client):
        client.post('/items', json={'name': 'Widget A', 'description': 'A useful widget'})
        response = client.get('/items')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['items']) == 1
        assert data['items'][0]['name'] == 'Widget A'


class TestCreateItem:
    def test_create_item_success(self, client):
        response = client.post('/items', json={'name': 'Test Item', 'description': 'A test description'})
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Test Item'
        assert 'id' in data
        assert 'created_at' in data

    def test_create_item_missing_name(self, client):
        response = client.post('/items', json={'description': 'A test description'})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'name' in data['error'].lower()

    def test_create_item_missing_description(self, client):
        response = client.post('/items', json={'name': 'Test Item'})
        assert response.status_code == 400

    def test_create_item_empty_json(self, client):
        response = client.post('/items', json={})
        assert response.status_code == 400

    def test_create_multiple_items(self, client):
        client.post('/items', json={'name': 'Item 1', 'description': 'First item'})
        response = client.post('/items', json={'name': 'Item 2', 'description': 'Second item'})
        assert response.status_code == 201


class TestDeleteItem:
    def test_delete_item_success(self, client):
        create_response = client.post('/items', json={'name': 'Item to Delete', 'description': 'Goodbye'})
        item_id = json.loads(create_response.data)['id']
        response = client.delete(f'/items/{item_id}')
        assert response.status_code == 200
        get_response = client.get(f'/items/{item_id}')
        assert get_response.status_code == 404

    def test_delete_item_not_found(self, client):
        response = client.delete('/items/nonexistent-id')
        assert response.status_code == 404

    def test_delete_twice(self, client):
        create_response = client.post('/items', json={'name': 'Item', 'description': 'Test'})
        item_id = json.loads(create_response.data)['id']
        client.delete(f'/items/{item_id}')
        response = client.delete(f'/items/{item_id}')
        assert response.status_code == 404


class TestEndpointNotFound:
    def test_invalid_endpoint(self, client):
        response = client.get('/invalid')
        assert response.status_code == 404

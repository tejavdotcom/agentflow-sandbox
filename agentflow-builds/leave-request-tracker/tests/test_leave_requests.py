import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture()
def setup_and_teardown():
    # Clear the in-memory storage before each test
    app.leave_requests.clear()
    app.employees.clear()
    yield


def test_submit_leave_request(setup_and_teardown):
    response = client.post('/leave-requests', json={
        'id': 1,
        'employee_id': 1,
        'start_date': '2023-10-01',
        'end_date': '2023-10-05',
        'type': 'vacation',
        'reason': 'Family trip'
    })
    assert response.status_code == 200
    assert response.json()['status'] == 'pending'


def test_submit_leave_request_invalid_type(setup_and_teardown):
    response = client.post('/leave-requests', json={
        'id': 2,
        'employee_id': 1,
        'start_date': '2023-10-01',
        'end_date': '2023-10-05',
        'type': 'invalid_type',
        'reason': 'Family trip'
    })
    assert response.status_code == 422


def test_approve_leave_request(setup_and_teardown):
    client.post('/leave-requests', json={
        'id': 3,
        'employee_id': 1,
        'start_date': '2023-10-01',
        'end_date': '2023-10-05',
        'type': 'vacation',
        'reason': 'Family trip'
    })
    response = client.patch('/leave-requests/3', json={'comment': 'Approved'})
    assert response.status_code == 200
    assert response.json()['status'] == 'approved'
    assert response.json()['comment'] == 'Approved'


def test_reject_leave_request(setup_and_teardown):
    client.post('/leave-requests', json={
        'id': 4,
        'employee_id': 1,
        'start_date': '2023-10-01',
        'end_date': '2023-10-05',
        'type': 'vacation',
        'reason': 'Family trip'
    })
    response = client.patch('/leave-requests/4', json={})
    assert response.status_code == 200
    assert response.json()['status'] == 'rejected'
    assert response.json()['comment'] is None


def test_approve_nonexistent_request(setup_and_teardown):
    response = client.patch('/leave-requests/999', json={'comment': 'Approved'})
    assert response.status_code == 404


def test_view_leave_balance(setup_and_teardown):
    app.employees[1] = {'id': 1, 'name': 'John Doe', 'leave_balance': 20}
    response = client.get('/leave-balance')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['leave_balance'] == 20


def test_view_leave_balance_empty(setup_and_teardown):
    response = client.get('/leave-balance')
    assert response.status_code == 200
    assert response.json() == []
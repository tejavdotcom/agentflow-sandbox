import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.parametrize('start_date, end_date, leave_type, reason, expected_status', [
    ('2023-10-01', '2023-10-05', 'vacation', 'Family trip', 201),
    ('2023-10-10', '2023-10-12', 'sick', 'Flu', 201),
    ('2023-10-15', '2023-10-20', 'personal', 'Personal matters', 201),
    ('2023-10-01', '2023-09-30', 'vacation', 'Invalid dates', 400),
    ('2023-10-01', '2023-10-05', 'holiday', 'Invalid type', 400)
])
def test_submit_leave_request(start_date, end_date, leave_type, reason, expected_status):
    response = client.post('/leave-request', json={
        'start_date': start_date,
        'end_date': end_date,
        'type': leave_type,
        'reason': reason
    })
    assert response.status_code == expected_status

@pytest.mark.parametrize('request_id, action, comment, expected_status', [
    (1, 'approve', 'Approved for vacation', 200),
    (1, 'reject', 'Not enough notice', 200),
    (999, 'approve', 'Invalid request', 404),
    (1, 'invalid_action', 'Invalid action', 400)
])
def test_approve_or_reject_leave_request(request_id, action, comment, expected_status):
    response = client.patch(f'/leave-request/{request_id}', json={
        'action': action,
        'comment': comment
    })
    assert response.status_code == expected_status

def test_view_remaining_leave_balance():
    response = client.get('/leave-balance')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    for employee in response.json():
        assert 'total_days' in employee
        assert 'remaining_balance' in employee

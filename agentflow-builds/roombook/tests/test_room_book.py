import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(scope='module')
def setup_module():
    # Setup initial data for tests
    response = client.post('/rooms', json={'name': 'Conference Room', 'floor': 1, 'capacity': 10, 'equipment': ['projector', 'whiteboard']})
    room_id = response.json()['id']
    client.post('/bookings', json={'room_id': room_id, 'title': 'Initial Booking', 'organiser_email': 'employee@example.com', 'start_time': '2023-10-10T10:00:00', 'end_time': '2023-10-10T11:00:00'})  # Create a booking for the test user
    return room_id

# Test adding a room

def test_add_room():
    response = client.post('/rooms', json={'name': 'Meeting Room', 'floor': 2, 'capacity': 5, 'equipment': ['video-call']})
    assert response.status_code == 201
    assert response.json()['name'] == 'Meeting Room'

# Test deactivating a room

def test_deactivate_room(setup_module):
    response = client.delete(f'/rooms/{setup_module}')
    assert response.status_code == 204

# Test searching for rooms

def test_search_rooms(setup_module):
    response = client.get('/rooms?date=2023-10-10&start_time=10:00&end_time=11:00&min_capacity=5')
    assert response.status_code == 200
    assert len(response.json()) > 0

# Test booking a room

def test_book_room(setup_module):
    response = client.post('/bookings', json={'room_id': setup_module, 'title': 'Team Meeting', 'organiser_email': 'employee@example.com', 'start_time': '2023-10-10T10:00:00', 'end_time': '2023-10-10T11:00:00'})
    assert response.status_code == 201

# Test booking overlap

def test_booking_overlap(setup_module):
    client.post('/bookings', json={'room_id': setup_module, 'title': 'Another Meeting', 'organiser_email': 'employee@example.com', 'start_time': '2023-10-10T10:30:00', 'end_time': '2023-10-10T11:30:00'})
    response = client.post('/bookings', json={'room_id': setup_module, 'title': 'Conflict Meeting', 'organiser_email': 'employee@example.com', 'start_time': '2023-10-10T10:15:00', 'end_time': '2023-10-10T11:15:00'})
    assert response.status_code == 400

# Test booking outside office hours

def test_booking_outside_office_hours(setup_module):
    response = client.post('/bookings', json={'room_id': setup_module, 'title': 'Late Meeting', 'organiser_email': 'employee@example.com', 'start_time': '2023-10-10T21:00:00', 'end_time': '2023-10-10T22:00:00'})
    assert response.status_code == 400

# Test listing my bookings

def test_list_my_bookings():
    response = client.get('/my_bookings?organiser_email=employee@example.com')
    assert response.status_code == 200

# Test canceling a booking

def test_cancel_booking():
    response = client.delete('/bookings/1')  # Assuming booking ID 1 exists
    assert response.status_code == 404

# Test today board

def test_today_board():
    response = client.get('/today_board')
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
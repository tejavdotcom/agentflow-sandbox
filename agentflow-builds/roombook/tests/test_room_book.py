import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def setup_rooms():
    # Setup initial rooms for testing
    response = client.post('/rooms', json={"name": "Room A", "floor": 1, "capacity": 10, "equipment": ["projector"]})
    room_a_id = response.json()['id']
    response = client.post('/rooms', json={"name": "Room B", "floor": 1, "capacity": 5, "equipment": ["whiteboard"]})
    room_b_id = response.json()['id']
    return room_a_id, room_b_id

# Test adding a room

def test_add_room():
    response = client.post('/rooms', json={"name": "Room C", "floor": 2, "capacity": 15, "equipment": ["video-call"]})
    assert response.status_code == 201
    assert response.json()['name'] == "Room C"

# Test deactivating a room

def test_deactivate_room(setup_rooms):
    room_a_id, _ = setup_rooms
    response = client.delete(f'/rooms/{room_a_id}')
    assert response.status_code == 204
    response = client.get('/rooms/search', params={"date": "2023-10-10", "start_time": "10:00", "end_time": "11:00", "min_capacity": 1})
    assert room_a_id not in [room['id'] for room in response.json()]

# Test searching for available rooms

def test_search_available_rooms(setup_rooms):
    room_a_id, room_b_id = setup_rooms
    response = client.get('/rooms/search', params={"date": "2023-10-10", "start_time": "10:00", "end_time": "11:00", "min_capacity": 1})
    assert response.status_code == 200
    assert len(response.json()) == 2  # Both rooms should be available

# Test booking a room

def test_book_room(setup_rooms):
    room_a_id, _ = setup_rooms
    response = client.post('/bookings', json={"room_id": room_a_id, "title": "Meeting", "organiser_email": "employee@example.com", "start_time": "2023-10-10T10:00:00", "end_time": "2023-10-10T11:00:00"})
    assert response.status_code == 201
    assert response.json()['title'] == "Meeting"

# Test double booking

def test_double_booking(setup_rooms):
    room_a_id, _ = setup_rooms
    client.post('/bookings', json={"room_id": room_a_id, "title": "First Meeting", "organiser_email": "employee@example.com", "start_time": "2023-10-10T10:00:00", "end_time": "2023-10-10T11:00:00"})
    response = client.post('/bookings', json={"room_id": room_a_id, "title": "Second Meeting", "organiser_email": "employee@example.com", "start_time": "2023-10-10T10:30:00", "end_time": "2023-10-10T11:30:00"})
    assert response.status_code == 409

# Test booking outside office hours

def test_booking_outside_office_hours(setup_rooms):
    room_a_id, _ = setup_rooms
    response = client.post('/bookings', json={"room_id": room_a_id, "title": "Late Meeting", "organiser_email": "employee@example.com", "start_time": "2023-10-10T21:00:00", "end_time": "2023-10-10T22:00:00"})
    assert response.status_code == 403

# Test listing my bookings

def test_list_my_bookings(setup_rooms):
    room_a_id, _ = setup_rooms
    client.post('/bookings', json={"room_id": room_a_id, "title": "My Meeting", "organiser_email": "employee@example.com", "start_time": "2023-10-10T10:00:00", "end_time": "2023-10-10T11:00:00"})
    response = client.get('/my_bookings?organiser_email=employee@example.com')
    assert response.status_code == 200
    assert len(response.json()) == 1

# Test canceling a booking

def test_cancel_booking(setup_rooms):
    room_a_id, _ = setup_rooms
    booking_response = client.post('/bookings', json={"room_id": room_a_id, "title": "Meeting to Cancel", "organiser_email": "employee@example.com", "start_time": "2023-10-10T10:00:00", "end_time": "2023-10-10T11:00:00"})
    booking_id = booking_response.json()['id']
    response = client.delete(f'/bookings/{booking_id}')
    assert response.status_code == 204
    response = client.get('/my_bookings?organiser_email=employee@example.com')
    assert len(response.json()) == 0

# Test today board

def test_today_board(setup_rooms):
    response = client.get('/today_board')
    assert response.status_code == 200
    assert len(response.json()) == 2  # Both rooms should be listed
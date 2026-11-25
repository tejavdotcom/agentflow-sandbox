from __future__ import annotations
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime, time
from typing import List, Dict, Optional

app = FastAPI()

class Room(BaseModel):
    id: int
    name: str
    floor: int
    capacity: int
    equipment: List[str]
    is_active: bool = True

class Booking(BaseModel):
    id: int
    room_id: int
    title: str
    organiser_email: str
    start_time: datetime
    end_time: datetime

class RoomCreate(BaseModel):
    name: str
    floor: int
    capacity: int
    equipment: List[str]

class BookingCreate(BaseModel):
    room_id: int
    title: str
    organiser_email: str
    start_time: datetime
    end_time: datetime

class SearchParams(BaseModel):
    date: str
    start_time: str
    end_time: str
    min_capacity: int
    required_equipment: Optional[List[str]] = None

rooms: Dict[int, Room] = {}
bookings: Dict[int, Booking] = {}
room_id_counter = 1
booking_id_counter = 1

@app.post('/rooms', status_code=201)
async def add_room(room: RoomCreate):
    global room_id_counter
    new_room = Room(id=room_id_counter, **room.dict())
    rooms[room_id_counter] = new_room
    room_id_counter += 1
    return new_room

@app.delete('/rooms/{room_id}', status_code=204)
async def deactivate_room(room_id: int):
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail='room not found')
    rooms[room_id].is_active = False

@app.get('/rooms/search', response_model=List[Room])
async def search_rooms(params: SearchParams):
    date = datetime.fromisoformat(params.date)
    start_time = datetime.fromisoformat(params.start_time)
    end_time = datetime.fromisoformat(params.end_time)
    available_rooms = []
    for room in rooms.values():
        if room.is_active and room.capacity >= params.min_capacity:
            is_free = True
            for booking in bookings.values():
                if booking.room_id == room.id:
                    if not (end_time <= booking.start_time or start_time >= booking.end_time):
                        is_free = False
                        break
            if is_free:
                available_rooms.append(room)
    return available_rooms

@app.post('/bookings', status_code=201)
async def book_room(booking: BookingCreate):
    global booking_id_counter
    if booking.start_time < datetime.now():
        raise HTTPException(status_code=400, detail='booking in the past')
    if booking.start_time.time() < time(8, 0) or booking.end_time.time() > time(20, 0):
        raise HTTPException(status_code=403, detail='booking outside office hours')
    if (booking.end_time - booking.start_time).total_seconds() < 900 or (booking.end_time - booking.start_time).total_seconds() > 14400:
        raise HTTPException(status_code=403, detail='booking duration invalid')
    for existing_booking in bookings.values():
        if existing_booking.room_id == booking.room_id:
            if not (booking.end_time <= existing_booking.start_time or booking.start_time >= existing_booking.end_time):
                raise HTTPException(status_code=409, detail='room already booked')
    new_booking = Booking(id=booking_id_counter, **booking.dict())
    bookings[booking_id_counter] = new_booking
    booking_id_counter += 1
    return new_booking

@app.get('/my_bookings', response_model=List[Booking])
async def list_my_bookings(organiser_email: str):
    user_bookings = [b for b in bookings.values() if b.organiser_email == organiser_email]
    return user_bookings  # Return empty list instead of raising 404

@app.delete('/bookings/{booking_id}', status_code=204)
async def cancel_booking(booking_id: int):
    if booking_id not in bookings:
        raise HTTPException(status_code=404, detail='booking not found')
    del bookings[booking_id]

@app.get('/today_board', response_model=List[Room])
async def today_board():
    return [room for room in rooms.values() if room.is_active]  # Only return active rooms

@app.get('/', include_in_schema=False)
async def read_index():
    return HTMLResponse(open('app/static/index.html').read())
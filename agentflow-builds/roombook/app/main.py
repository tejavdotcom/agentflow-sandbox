from __future__ import annotations
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from datetime import datetime, time, timedelta
from typing import List, Optional, Dict, Any

app = FastAPI()

class Room(BaseModel):
    id: int = Field(default=None)
    name: str
    floor: int
    capacity: int
    equipment: List[str]
    is_active: bool = True

class Booking(BaseModel):
    id: int = Field(default=None)
    room_id: int
    title: str
    organiser_email: str
    start_time: datetime
    end_time: datetime

rooms: Dict[int, Room] = {}
bookings: Dict[int, Booking] = {}
room_id_counter = 1
booking_id_counter = 1

@app.post('/rooms', status_code=201)
async def add_room(room: Room):
    global room_id_counter
    room.id = room_id_counter
    rooms[room_id_counter] = room
    room_id_counter += 1
    return room

@app.delete('/rooms/{room_id}', status_code=204)
async def deactivate_room(room_id: int):
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail='room not found')
    rooms[room_id].is_active = False

@app.get('/rooms', response_model=List[Room])
async def search_rooms(
    date: str,
    start_time: str,
    end_time: str,
    min_capacity: int,
    required_equipment: Optional[List[str]] = Query(None)
):
    start_dt = datetime.fromisoformat(f'{date}T{start_time}')
    end_dt = datetime.fromisoformat(f'{date}T{end_time}')
    available_rooms = []
    for room in rooms.values():
        if room.is_active and room.capacity >= min_capacity:
            if not any(
                booking.room_id == room.id and
                not (end_dt <= booking.start_time or start_dt >= booking.end_time)
                for booking in bookings.values()
            ):
                if required_equipment is None or all(eq in room.equipment for eq in required_equipment):
                    available_rooms.append(room)
    return available_rooms

@app.post('/bookings', status_code=201)
async def book_room(booking: Booking):
    global booking_id_counter
    if booking.start_time < datetime.now():
        raise HTTPException(status_code=400, detail='booking in the past')
    if booking.start_time.time() < time(8, 0) or booking.end_time.time() > time(20, 0):
        raise HTTPException(status_code=400, detail='outside office hours')
    if (booking.end_time - booking.start_time) < timedelta(minutes=15) or (booking.end_time - booking.start_time) > timedelta(hours=4):
        raise HTTPException(status_code=400, detail='invalid booking duration')
    if booking.room_id not in rooms or not rooms[booking.room_id].is_active:
        raise HTTPException(status_code=400, detail='invalid room')
    if any(
        b.room_id == booking.room_id and
        not (booking.end_time <= b.start_time or booking.start_time >= b.end_time)
        for b in bookings.values()
    ):
        raise HTTPException(status_code=400, detail='booking overlaps')
    booking.id = booking_id_counter
    bookings[booking_id_counter] = booking
    booking_id_counter += 1
    return booking

@app.get('/my_bookings', response_model=List[Booking])
async def list_my_bookings(organiser_email: str):
    user_bookings = [b for b in bookings.values() if b.organiser_email == organiser_email]
    if not user_bookings:
        raise HTTPException(status_code=404, detail='no bookings found')
    return user_bookings

@app.delete('/bookings/{booking_id}', status_code=204)
async def cancel_booking(booking_id: int):
    if booking_id not in bookings:
        raise HTTPException(status_code=404, detail='booking not found')
    del bookings[booking_id]

@app.get('/today_board', response_model=Dict[str, Any])
async def today_board():
    today = datetime.now().date()
    board = {room_id: {'room': room, 'bookings': []} for room_id, room in rooms.items() if room.is_active}
    for booking in bookings.values():
        if booking.start_time.date() == today:
            board[booking.room_id]['bookings'].append(booking.dict())  # Ensure booking is serialized correctly
    return board

@app.get('/', response_class=HTMLResponse, include_in_schema=False)
async def read_index():
    with open('app/static/index.html') as f:
        return f.read()
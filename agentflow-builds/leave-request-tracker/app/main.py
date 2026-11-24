from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()

# In-memory storage
app.leave_requests = []
app.employees = {}

class LeaveRequest(BaseModel):
    id: int
    employee_id: int
    start_date: str
    end_date: str
    type: str = Field(..., pattern='^(vacation|sick|personal)$')
    reason: str
    status: str = 'pending'
    comment: Optional[str] = None

class Employee(BaseModel):
    id: int
    name: str
    leave_balance: int = 20

@app.post('/leave-requests', response_model=LeaveRequest)
async def submit_leave_request(request: LeaveRequest):
    app.leave_requests.append(request)
    return request

@app.patch('/leave-requests/{id}', response_model=LeaveRequest)
async def approve_or_reject_request(id: int, comment: Optional[str] = None):
    for request in app.leave_requests:
        if request.id == id:
            request.status = 'approved' if comment else 'rejected'
            request.comment = comment
            return request
    raise HTTPException(status_code=404, detail='Leave request not found')

@app.get('/leave-balance', response_model=List[Employee])
async def get_leave_balance():
    return list(app.employees.values())

@app.get('/', response_class=HTMLResponse, include_in_schema=False)
async def read_root():
    with open('app/static/index.html') as f:
        return f.read()
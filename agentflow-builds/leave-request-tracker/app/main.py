from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class LeaveRequest(BaseModel):
    start_date: str
    end_date: str
    type: str
    reason: str

@app.post('/leave-request')
async def submit_leave_request(request: LeaveRequest):
    if request.end_date <= request.start_date:
        raise HTTPException(status_code=400, detail='End date must be after start date.')
    # Logic to handle leave request submission
    return {'status': 'success', 'message': 'Leave request submitted.'}

@app.patch('/leave-request/{id}')
async def approve_or_reject_leave_request(id: int, action: str, comment: str):
    # Logic to approve or reject leave request
    return {'status': 'success', 'message': 'Leave request updated.'}

@app.get('/leave-balance')
async def view_remaining_leave_balance():
    # Logic to retrieve leave balances
    return [{'total_days': 20, 'remaining_balance': 15}]
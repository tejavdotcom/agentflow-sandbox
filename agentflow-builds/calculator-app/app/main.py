from __future__ import annotations
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI()

class CalculationInput(BaseModel):
    num1: float = Field(..., description='First number')
    num2: float = Field(..., description='Second number')

class CalculationResult(BaseModel):
    result: float

calculations = {}  # In-memory storage

@app.post('/add', response_model=CalculationResult)
async def add(input: CalculationInput):
    result = input.num1 + input.num2
    calculations['add'] = result  # Persisting result
    return CalculationResult(result=result)

@app.post('/subtract', response_model=CalculationResult)
async def subtract(input: CalculationInput):
    result = input.num1 - input.num2
    calculations['subtract'] = result  # Persisting result
    return CalculationResult(result=result)

@app.post('/multiply', response_model=CalculationResult)
async def multiply(input: CalculationInput):
    result = input.num1 * input.num2
    calculations['multiply'] = result  # Persisting result
    return CalculationResult(result=result)

@app.post('/divide', response_model=CalculationResult)
async def divide(input: CalculationInput):
    if input.num2 == 0:
        raise HTTPException(status_code=400, detail='division by zero')
    result = input.num1 / input.num2
    calculations['divide'] = result  # Persisting result
    return CalculationResult(result=result)

@app.get('/', include_in_schema=False)
async def read_root():
    return HTMLResponse(open('app/static/index.html').read())
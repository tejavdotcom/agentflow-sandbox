import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test addition

def test_add_valid():
    response = client.post('/add', json={'num1': 1.5, 'num2': 2.5})
    assert response.status_code == 200
    assert response.json() == {'result': 4.0}


def test_add_invalid_input():
    response = client.post('/add', json={'num1': 'a', 'num2': 2.5})
    assert response.status_code == 422

# Test subtraction

def test_subtract_valid():
    response = client.post('/subtract', json={'num1': 5.0, 'num2': 3.0})
    assert response.status_code == 200
    assert response.json() == {'result': 2.0}


def test_subtract_invalid_input():
    response = client.post('/subtract', json={'num1': 5.0, 'num2': 'b'})
    assert response.status_code == 422

# Test multiplication

def test_multiply_valid():
    response = client.post('/multiply', json={'num1': 3.0, 'num2': 4.0})
    assert response.status_code == 200
    assert response.json() == {'result': 12.0}


def test_multiply_invalid_input():
    response = client.post('/multiply', json={'num1': 'c', 'num2': 4.0})
    assert response.status_code == 422

# Test division

def test_divide_valid():
    response = client.post('/divide', json={'num1': 10.0, 'num2': 2.0})
    assert response.status_code == 200
    assert response.json() == {'result': 5.0}


def test_divide_by_zero():
    response = client.post('/divide', json={'num1': 10.0, 'num2': 0})
    assert response.status_code == 400
    assert response.json() == {'detail': 'division by zero'}


def test_divide_invalid_input():
    response = client.post('/divide', json={'num1': 10.0, 'num2': 'd'})
    assert response.status_code == 422
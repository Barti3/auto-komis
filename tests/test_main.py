from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "AutoMarket" in response.text

def test_car_list():
    response = client.get("/login")
    assert response.status_code == 200

def test_register_page():
    response = client.get("/register")
    assert response.status_code == 200

import pytest
import os
import sys
import time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

# 1. Konfiguracja ścieżek dla Dockera
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import main
from main import app, Base, User, Car, RoleEnum

# 2. Parametry połączenia z docker-compose.yml
DB_USER = "bartek"
DB_PASS = "mojehaslo"
DB_HOST = "mariadb"
DB_NAME = "auto_komis"

DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/{DB_NAME}"

engine = create_engine(DB_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ==============================================================================
# FIXTURES - ZARZĄDZANIE BAZĄ I SESJĄ
# ==============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_db_schema():
    """Tworzy tabele w MariaDB przed wszystkimi testami."""
    for _ in range(15):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except exc.OperationalError:
            time.sleep(1)
    pytest.exit("Błąd: Nie można połączyć się z MariaDB.")

@pytest.fixture(scope="function")
def db_session():
    """Uruchamia transakcję i robi ROLLBACK po każdym teście."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    main.SessionLocal = lambda: session

    yield session

    session.close()
    transaction.rollback() #
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def setup_mocks(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr(main, "get_geo", lambda ip: ("Solec Kujawski", "KP", "PL"))
    monkeypatch.setattr(main, "send_to_queue", lambda queue, msg: None)

# ==============================================================================
# PAKIET 14 TESTÓW
# ==============================================================================

def test_root_status(client):
    assert client.get("/").status_code == 200

def test_register_page_loads(client):
    assert client.get("/register").status_code == 200

def test_register_user_success(client):
    response = client.post("/register", data={
        "username": "nowy_user", "password": "1", "confirm_password": "1"
    }, follow_redirects=False)
    assert response.status_code == 302

def test_register_passwords_mismatch(client):
    response = client.post("/register", data={"username": "u2", "password": "1", "confirm_password": "3"})
    assert "Hasła nie są identyczne" in response.text

def test_register_existing_user(client):
    payload = {"username": "zajety", "password": "1", "confirm_password": "1"}
    client.post("/register", data=payload)
    assert "Użytkownik o tej nazwie już istnieje" in client.post("/register", data=payload).text

def test_login_invalid_credentials(client):
    client.post("/register", data={"username": "fabi", "password": "1", "confirm_password": "1"})
    assert "Niepoprawne dane logowania" in client.post("/login", data={"username": "fabi", "password": "z"}).text

def test_login_success_seller(client):
    client.post("/register", data={"username": "s1", "password": "1", "confirm_password": "1"})
    res = client.post("/login", data={"username": "s1", "password": "1"}, follow_redirects=False)
    assert res.status_code == 302

def test_logout(client):
    assert client.get("/logout", follow_redirects=False).status_code == 302

def test_add_car_success(client):
    client.post("/register", data={"username": "d", "password": "1", "confirm_password": "1"})
    client.post("/login", data={"username": "d", "password": "1"})
    car = {"title": "T", "price": 1, "year": 20, "mileage": 1, "brand": "T", "model": "T", "fuel": "T", "engine": "T", "condition": "T", "description": "T"}
    files = [("images", ("a.jpg", b"f", "image/jpeg"))]
    assert client.post("/seller/car/add", data=car, files=files, follow_redirects=False).status_code == 303

# POPRAWIONY TEST LIMITU ZDJĘĆ
def test_add_car_limit_exceeded(client):
    client.post("/register", data={"username": "p", "password": "1", "confirm_password": "1"})
    client.post("/login", data={"username": "p", "password": "1"})
    # Musimy podać kompletne dane, żeby przejść walidację
    car = {"title": "T", "price": 1, "year": 20, "mileage": 1, "brand": "T", "model": "T", "fuel": "T", "engine": "T", "condition": "T", "description": "T"}
    files = [("images", (f"i{i}.jpg", b"f", "image/jpeg")) for i in range(51)]
    response = client.post("/seller/car/add", data=car, files=files)
    assert response.status_code == 400

def test_unauthenticated_redirect(client):
    assert client.get("/seller", follow_redirects=False).status_code == 303

def test_seller_forbidden_admin(client):
    client.post("/register", data={"username": "u", "password": "1", "confirm_password": "1"})
    client.post("/login", data={"username": "u", "password": "1"})
    assert "Brak uprawnień" in client.get("/admin").text

def test_add_car_bad_data(client):
    client.post("/register", data={"username": "h", "password": "1", "confirm_password": "1"})
    client.post("/login", data={"username": "h", "password": "1"})
    assert client.post("/seller/car/add", data={"year": 1}).status_code == 422

def test_delete_404(client):
    client.post("/register", data={"username": "c", "password": "1", "confirm_password": "1"})
    client.post("/login", data={"username": "c", "password": "1"})
    assert client.get("/seller/car/delete/999").status_code == 404

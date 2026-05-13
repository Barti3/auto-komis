import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ==============================================================================
# KONFIGURACJA ŚRODOWISKA TESTOWEGO
# ==============================================================================

# Dynamiczne dodanie ścieżki nadrzędnej, aby testy widziały plik main.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import main
from main import app, Base, User, Car, RoleEnum

# Inicjalizacja bazy SQLite w pamięci RAM (StaticPool współdzieli dane między wątkami)
# Rozwiązuje to problem 'readonly database' wewnątrz kontenerów Docker
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Podpięcie testowej bazy pod oryginalną aplikację
main.engine = engine
main.SessionLocal = TestingSessionLocal

# ==============================================================================
# FIXTURES (Przygotowanie przed każdym testem)
# ==============================================================================

@pytest.fixture
def client():
    """Tworzy odizolowanego klienta testowego (czyści ciasteczka sesji)."""
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def setup_database(monkeypatch, tmp_path):
    """Automatycznie przygotowuje czystą bazę danych i atrapy (mocki) usług."""
    Base.metadata.create_all(bind=engine)
    
    # Mockowanie usług zewnętrznych, aby nie polegać na API czy RabbitMQ
    monkeypatch.setattr(main, "UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr(main, "get_geo", lambda ip: ("Solec", "Kujawskie", "Poland"))
    monkeypatch.setattr(main, "send_to_queue", lambda queue, msg: None)
    
    yield
    
    Base.metadata.drop_all(bind=engine)

# ==============================================================================
# TESTY FUNKCJONALNE (HAPPY PATH)
# ==============================================================================

def test_root_status(client):
    """Sprawdzenie dostępności strony głównej."""
    response = client.get("/")
    assert response.status_code == 200

def test_register_page_loads(client):
    """Weryfikacja renderowania formularza rejestracji."""
    response = client.get("/register")
    assert response.status_code == 200

def test_register_user_success(client):
    """Prawidłowy proces rejestracji nowego użytkownika."""
    response = client.post("/register", data={
        "username": "nowy_user",
        "password": "haslo123",
        "confirm_password": "haslo123"
    }, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/login"

def test_register_passwords_mismatch(client):
    """Błąd przy rejestracji: hasła nie są identyczne."""
    response = client.post("/register", data={
        "username": "user2", "password": "123", "confirm_password": "321"
    })
    assert "Hasła nie są identyczne" in response.text

def test_register_existing_user(client):
    """Błąd przy rejestracji: nazwa użytkownika jest już zajęta."""
    payload = {"username": "zajety", "password": "123", "confirm_password": "123"}
    client.post("/register", data=payload)
    response = client.post("/register", data=payload)
    assert "Użytkownik o tej nazwie już istnieje" in response.text

def test_login_invalid_credentials(client):
    """Odrzucenie logowania przy błędnych danych."""
    client.post("/register", data={"username": "fabi", "password": "123", "confirm_password": "123"})
    response = client.post("/login", data={"username": "fabi", "password": "zle"})
    assert "Niepoprawne dane logowania" in response.text

def test_login_success_seller(client):
    """Prawidłowe logowanie z rolą sprzedawcy."""
    client.post("/register", data={"username": "seller1", "password": "123", "confirm_password": "123"})
    response = client.post("/login", data={"username": "seller1", "password": "123"}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/seller"

def test_logout(client):
    """Wylogowanie użytkownika i czyszczenie sesji."""
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/"

def test_add_car_success(client):
    """Dodanie ogłoszenia sprzedaży wraz z wgraniem zdjęcia."""
    client.post("/register", data={"username": "dealer", "password": "123", "confirm_password": "123"})
    client.post("/login", data={"username": "dealer", "password": "123"})
    
    car_data = {
        "title": "Toyota Yaris", "price": 15000, "year": 2010, "mileage": 100000,
        "brand": "Toyota", "model": "Yaris", "fuel": "Benzyna", "engine": "1.0",
        "condition": "Używany", "description": "Super stan"
    }
    files = [("images", ("auto.jpg", b"fake_data", "image/jpeg"))]
    response = client.post("/seller/car/add", data=car_data, files=files, follow_redirects=False)
    assert response.status_code == 303 

def test_add_car_limit_exceeded(client):
    """Weryfikacja limitu zdjęć (maksymalnie 50 na ogłoszenie)."""
    client.post("/register", data={"username": "limiter", "password": "123", "confirm_password": "123"})
    client.post("/login", data={"username": "limiter", "password": "123"})
    
    car_data = {"title": "X", "price": 1, "year": 2000, "mileage": 1, "brand": "X", "model": "X", "fuel": "X", "engine": "X", "condition": "X", "description": "X"}
    files = [("images", (f"i{i}.jpg", b"f", "image/jpeg")) for i in range(51)]
    
    response = client.post("/seller/car/add", data=car_data, files=files)
    assert response.status_code == 400
    assert response.json() == {"detail": "Maksymalnie 50 zdjęć"}

# ==============================================================================
# TESTY BEZPIECZEŃSTWA (EDGE CASES)
# ==============================================================================

def test_unauthenticated_user_redirected(client):
    """Blokada dostępu do panelu sprzedawcy dla osób niezalogowanych."""
    response = client.get("/seller", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"

def test_seller_cannot_access_admin_panel(client):
    """Blokada dostępu do panelu admina dla zwykłego sprzedawcy."""
    client.post("/register", data={"username": "user", "password": "123", "confirm_password": "123"})
    client.post("/login", data={"username": "user", "password": "123"})
    response = client.get("/admin")
    assert "Brak uprawnień do panelu admina" in response.text

def test_add_car_missing_data(client):
    """Walidacja formularza: odrzucenie przy brakujących wymaganych polach."""
    client.post("/register", data={"username": "hacker", "password": "123", "confirm_password": "123"})
    client.post("/login", data={"username": "hacker", "password": "123"})
    response = client.post("/seller/car/add", data={"year": 2020}) 
    assert response.status_code == 422

def test_delete_nonexistent_car(client):
    """Obsługa błędnego ID przy próbie usunięcia ogłoszenia."""
    client.post("/register", data={"username": "cleaner", "password": "123", "confirm_password": "123"})
    client.post("/login", data={"username": "cleaner", "password": "123"})
    response = client.get("/seller/car/delete/99999", follow_redirects=False)
    assert response.status_code == 404

import pytest
import os
import sys
import time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

# 1. Konfiguracja ścieżek dla środowiska Docker/Jenkins
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import main
from main import app, Base

# 2. Dane połączenia zgodne z siecią w Docker Compose
# Używamy hosta 'mariadb', bo tak nazywa się usługa w sieci Dockera
DB_URL = "mysql+pymysql://bartek:mojehaslo@mariadb:3306/auto_komis"

engine = create_engine(DB_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ==============================================================================
# FIXTURES - ZARZĄDZANIE BAZĄ I SESJĄ
# ==============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Weryfikacja połączenia i inicjalizacja tabel przed startem testów."""
    for _ in range(15):  # Czekamy max 15 sekund na bazę
        try:
            Base.metadata.create_all(bind=engine)
            return
        except exc.OperationalError:
            time.sleep(1)
    pytest.exit("Błąd: Nie można połączyć się z MariaDB w sieci Dockera.")

@pytest.fixture(scope="function")
def client():
    """Zarządzanie sesją z automatycznym wycofaniem zmian (rollback)."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    # Podmieniamy sesję w głównej aplikacji na tę testową
    main.SessionLocal = lambda: session
    
    with TestClient(app) as c:
        yield c
    
    session.close()
    transaction.rollback()  # To sprawia, że baza po testach jest czysta
    connection.close()

@pytest.fixture(autouse=True)
def setup_mocks(monkeypatch, tmp_path):
    """Atrapy usług zewnętrznych, aby testy były niezależne od internetu."""
    monkeypatch.setattr(main, "UPLOAD_DIR", str(tmp_path))
    # Dane lokalizacji (Twoje okolice Solec Kujawski/KP)
    monkeypatch.setattr(main, "get_geo", lambda ip: ("Solec Kujawski", "KP", "PL"))
    monkeypatch.setattr(main, "send_to_queue", lambda queue, msg: None)

# ==============================================================================
# PAKIET 14 TESTÓW INTEGRACYJNYCH
# ==============================================================================

# 1. Test dostępności strony głównej
def test_root_status(client):
    assert client.get("/").status_code == 200

# 2. Test ładowania strony rejestracji
def test_register_page_loads(client):
    assert client.get("/register").status_code == 200

# 3. Test poprawnej rejestracji (powinien przekierować)
def test_register_user_success(client):
    response = client.post("/register", data={
        "username": "tester1", "password": "1", "confirm_password": "1"
    }, follow_redirects=False)
    assert response.status_code == 302

# 4. Test błędu przy niezgodnych hasłach
def test_register_passwords_mismatch(client):
    response = client.post("/register", data={
        "username": "u", "password": "1", "confirm_password": "2"
    })
    assert "Hasła nie są identyczne" in response.text

# 5. Test błędu przy zajętym loginie
def test_register_existing_user(client):
    p = {"username": "zajety", "password": "1", "confirm_password": "1"}
    client.post("/register", data=p)
    assert "Użytkownik o tej nazwie już istnieje" in client.post("/register", data=p).text

# 6. Test logowania z błędnymi danymi
def test_login_invalid_credentials(client):
    client.post("/register", data={"username": "a", "password": "1", "confirm_password": "1"})
    assert "Niepoprawne dane logowania" in client.post("/login", data={"username": "a", "password": "x"}).text

# 7. Test poprawnego logowania sprzedawcy
def test_login_success_seller(client):
    client.post("/register", data={"username": "s", "password": "1", "confirm_password": "1"})
    res = client.post("/login", data={"username": "s", "password": "1"}, follow_redirects=False)
    assert res.status_code == 302

# 8. Test wylogowania
def test_logout(client):
    assert client.get("/logout", follow_redirects=False).status_code == 302

# 9. Test poprawnego dodania auta
def test_add_car_success(client):
    client.post("/register", data={"username": "d", "password": "1", "confirm_password": "1"})
    client.post("/login", data={"username": "d", "password": "1"})
    car = {"title": "T", "price": 1, "year": 20, "mileage": 1, "brand": "T", "model": "T", "fuel": "T", "engine": "T", "condition": "T", "description": "T"}
    files = [("images", ("auto.jpg", b"fakecontent", "image/jpeg"))]
    assert client.post("/seller/car/add", data=car, files=files, follow_redirects=False).status_code == 303

# 10. Test przekroczenia limitu 50 zdjęć
def test_add_car_limit_exceeded(client):
    client.post("/register", data={"username": "p", "password": "1", "confirm_password": "1"})
    client.post("/login", data={"username": "p", "password": "1"})
    car = {"title": "T", "price": 1, "year": 20, "mileage": 1, "brand": "T", "model": "T", "fuel": "T", "engine": "T", "condition": "T", "description": "T"}
    files = [("images", (f"img{i}.jpg", b"f", "image/jpeg")) for i in range(51)]
    assert client.post("/seller/car/add", data=car, files=files).status_code == 400

# 11. Test przekierowania niezalogowanego z panelu sprzedawcy
def test_unauthenticated_redirect(client):
    assert client.get("/seller", follow_redirects=False).status_code == 303

# 12. Test blokady panelu admina dla zwykłego usera
def test_seller_forbidden_admin(client):
    client.post("/register", data={"username": "u", "password": "1", "confirm_password": "1"})
    client.post("/login", data={"username": "u", "password": "1"})
    assert "Brak uprawnień" in client.get("/admin").text

# 13. Test walidacji danych (błędny typ/brakujące pola)
def test_add_car_bad_data(client):
    client.post("/register", data={"username": "h", "password": "1", "confirm_password": "1"})
    client.post("/login", data={"username": "h", "password": "1"})
    # Przesyłamy tylko rok, brakuje tytułu i ceny - FastAPI zwróci 422
    assert client.post("/seller/car/add", data={"year": 1}).status_code == 422

# 14. Test usuwania nieistniejącego auta
def test_delete_404(client):
    client.post("/register", data={"username": "c", "password": "1", "confirm_password": "1"})
    client.post("/login", data={"username": "c", "password": "1"})
    assert client.get("/seller/car/delete/9999").status_code == 404

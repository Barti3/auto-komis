from fastapi import FastAPI, Request, Form, status, File, UploadFile, Path
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
from sqlalchemy import (
    create_engine, Column, Integer, String, Enum, Float, DateTime, func, or_, Text, ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, joinedload
import enum
import time
from fastapi import Header, HTTPException
from fastapi import WebSocket, WebSocketDisconnect
import requests
from datetime import datetime
import os
from fastapi.staticfiles import StaticFiles
from typing import List
import shutil

# ------------------------
# KONFIGURACJA
# ------------------------
API_KEY = "bartek"
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="CHANGE_ME_TO_A_RANDOM_SECRET")  # zmień w produkcji!
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
# ------------------------
# BAZA DANYCH
# ------------------------
DATABASE_URL = "mysql+pymysql://bartek:mojehaslo@mariadb-db:3306/auto_komis"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ------------------------
# MODELE
# ------------------------
class RoleEnum(str, enum.Enum):
    admin = "admin"
    seller = "seller"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)


class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=True)
    ip_address = Column(String(45), nullable=False)
    timestamp = Column(Float, default=lambda: time.time())
    success = Column(Integer, default=0)  # 0 = nieudane, 1 = udane
    locked_until = Column(Float, default=0.0)

class LoginMetadata(Base):
    __tablename__ = "login_metadata"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    ip_address = Column(String(45))
    city = Column(String(100))
    region = Column(String(100))
    country = Column(String(100))
    screen_width = Column(Integer)
    screen_height = Column(Integer)
    timezone = Column(String(50))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    mileage = Column(Integer, nullable=False)

    brand = Column(String(100))
    model = Column(String(100))
    fuel = Column(String(50))
    engine = Column(String(50))

    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    images = relationship(
        "CarImage",
        back_populates="car",
        cascade="all, delete"
    )

class CarImage(Base):
    __tablename__ = "car_images"

    id = Column(Integer, primary_key=True)
    car_id = Column(Integer, ForeignKey("cars.id"))
    filename = Column(String(255), nullable=False)
    is_main = Column(Integer, default=0)

    car = relationship("Car", back_populates="images")

#Base.metadata.create_all(engine)  # uruchom raz, by utworzyć tabele

# ------------------------
# HASŁA — BEZPIECZNY KONTEKST
# ------------------------
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# ------------------------
# PARAMETRY BLOKADY
# ------------------------
MAX_ATTEMPTS = 5
WINDOW = 300
LOCKOUT_DURATION = 300

# ------------------------
# FUNKCJE BRUTE-FORCE (BAZA)
# ------------------------
def record_attempt(db, username: str, ip: str, success: bool):
    attempt = LoginAttempt(
        username=username,
        ip_address=ip,
        success=1 if success else 0,
        timestamp=time.time()
    )
    db.add(attempt)
    db.commit()


def get_recent_failures(db, username: str, ip: str):
    cutoff = time.time() - WINDOW
    return db.query(LoginAttempt).filter(
        LoginAttempt.ip_address == ip,
        LoginAttempt.success == 0,
        LoginAttempt.timestamp >= cutoff
    ).count()


def is_locked(db, username: str, ip: str) -> bool:
    now = time.time()
    record = db.query(LoginAttempt).filter(
        or_(LoginAttempt.username == username, LoginAttempt.ip_address == ip)
    ).order_by(LoginAttempt.id.desc()).first()
    return bool(record and record.locked_until and record.locked_until > now)


def lock_account(db, username: str, ip: str):
    now = time.time()
    lock_until = now + LOCKOUT_DURATION
    attempt = LoginAttempt(
        username=username,
        ip_address=ip,
        success=0,
        locked_until=lock_until,
        timestamp=now
    )
    db.add(attempt)
    db.commit()


def clear_old_attempts(db):
    """Czyszczenie bardzo starych prób, np. starszych niż 10*WINDOW."""
    cutoff = time.time() - (WINDOW * 10)
    db.query(LoginAttempt).filter(LoginAttempt.timestamp < cutoff).delete()
    db.commit()


# ------------------------
# SESJE / AUTORYZACJA
# ------------------------
def get_client_ip(request: Request) -> str:
    client = request.client
    return client.host if client else "unknown"


def require_auth(request: Request):
    user = request.session.get("user")
    role = request.session.get("role")
    if not user or not role:
        return None
    return {"user": user, "role": role}


#-------------------
# Funkcja geolokalizaji
#-------------------
def get_geo_from_ip(ip: str):
    try:
        r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=3)
        if r.status_code == 200:
            data = r.json()
            return {
                "city": data.get("city"),
                "region": data.get("region"),
                "country": data.get("country_name")
            }
    except Exception:
        pass

    return {"city": None, "region": None, "country": None}

import requests

def get_geo(ip: str):
    try:
        r = requests.get(
            f"http://ip-api.com/json/{ip}",
            timeout=5
        )
        data = r.json()

        if data.get("status") != "success":
            return None, None, None

        return (
            data.get("city"),
            data.get("regionName"),
            data.get("country")
        )

    except Exception as e:
        print("GEO ERROR:", e)
        return None, None, None

# ------------------------
# ROUTES
# ------------------------

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Ekran logowania"""
    user = request.session.get("user")
    role = request.session.get("role")

    if user and role:
        if role == "admin":
            return RedirectResponse(url="/admin")
        return RedirectResponse(url="/home")

    return templates.TemplateResponse("login.html", {"request": request, "error": ""})


@app.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    screen_width: int = Form(None),
    screen_height: int = Form(None),
    timezone: str = Form(None),
    user_agent: str = Form(None),
):
    username = username.strip()
    #ip = get_client_ip(request)
    # 🔴 TEST – wymuszone publiczne IP
    ip = "37.47.198.53"
    city, region, country = get_geo(ip)

    print("FINAL GEO:", city, region, country)
    # ip = get_client_ip(request)
    db = SessionLocal()

    clear_old_attempts(db)

    if is_locked(db, username, ip):
        db.close()
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Konto lub IP zablokowane."},
        )

    user = db.query(User).filter(User.username == username).first()

    if not user or not pwd_context.verify(password, user.password):
        record_attempt(db, username, ip, success=False)
        failures = get_recent_failures(db, username, ip)

        if failures >= MAX_ATTEMPTS:
            lock_account(db, username, ip)
            db.close()
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Zbyt wiele prób. Konto/IP zablokowane."},
            )

        db.close()
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Niepoprawne dane logowania."},
        )

    # ✅ SUKCES LOGOWANIA
    record_attempt(db, username, ip, success=True)

    #city, region, country = get_geo_from_ip(ip)

    metadata = LoginMetadata(
        username=username,
        ip_address=ip,
        city=city,
        region=region,
        country=country,
        screen_width=screen_width,
        screen_height=screen_height,
        timezone=timezone,
        user_agent=user_agent,
    )

    db.add(metadata)
    db.commit()

    request.session["user"] = username
    request.session["role"] = user.role
    db.close()

    if user.role == RoleEnum.admin:
        return RedirectResponse(url="/admin", status_code=302)
    return RedirectResponse(url="/seller", status_code=302)


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    """Ekran rejestracji nowego użytkownika"""
    return templates.TemplateResponse("register.html", {"request": request, "error": ""})


@app.post("/register", response_class=HTMLResponse)
def register_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    db: Session = SessionLocal()
    username = username.strip()
    password = password.strip()
    confirm_password = confirm_password.strip()

    # Sprawdź, czy użytkownik o tej nazwie już istnieje
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        db.close()
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Użytkownik o tej nazwie już istnieje."},
        )

    # Sprawdź zgodność haseł
    if password != confirm_password:
        db.close()
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Hasła nie są identyczne."},
        )

    # Zaszyfruj hasło (Twoim kontekstem pbkdf2_sha256)
    hashed_password = pwd_context.hash(password)

    # Utwórz nowego użytkownika z rolą 'user'
    new_user = User(username=username, password=hashed_password, role=RoleEnum.seller)
    db.add(new_user)
    db.commit()
    db.close()

    # Automatyczne logowanie po rejestracji
    #request.session["user"] = username
    #request.session["role"] = RoleEnum.user

    # Przekierowanie do panelu logowania
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@app.get("/admin", response_class=HTMLResponse)
def admin_view(request: Request):
    auth = require_auth(request)
    if not auth:
        return RedirectResponse(url="/")
    if auth["role"] != "admin":
        return templates.TemplateResponse(
            "forbidden.html", {"request": request, "message": "Brak uprawnień do panelu admina."}
        )
    return templates.TemplateResponse("admin.html", {"request": request, "user": auth["user"]})


@app.get("/admin/users", response_class=HTMLResponse)
def admin_users_view(request: Request):
    auth = require_auth(request)

    # Sprawdzenie, czy zalogowany jest admin
    if not auth or auth.get("role") != "admin":
        return RedirectResponse(url="/login")

    db: Session = SessionLocal()
    users = db.query(User).all()  # pobieramy wszystkich użytkowników
    db.close()

    return templates.TemplateResponse(
        "admin_users.html",
        {
            "request": request,
            "users": users,
            "current_admin_id": auth.get("user_id")  # do weryfikacji przy usuwaniu
        }
    )

@app.post("/admin/users/delete/{user_id}")
def admin_delete_user(user_id: int, request: Request):
    auth = require_auth(request)

    if not auth or auth.get("role") != "admin":
        return RedirectResponse(url="/login")

    db: Session = SessionLocal()
    user_to_delete = db.query(User).filter(User.id == user_id).first()

    if not user_to_delete:
        db.close()
        raise HTTPException(status_code=404, detail="Użytkownik nie istnieje")

    if user_to_delete.role == "admin":
        db.close()
        raise HTTPException(status_code=403, detail="Nie można usuwać adminów")

    # ✅ usuń wszystkie samochody użytkownika
    user_cars = db.query(Car).filter(Car.user_id == user_id).all()
    for car in user_cars:
        # usuń zdjęcia z dysku
        car_dir = os.path.join(UPLOAD_DIR, f"car_{car.id}")
        if os.path.exists(car_dir):
            shutil.rmtree(car_dir)
        db.delete(car)

    db.delete(user_to_delete)
    db.commit()
    db.close()

    return RedirectResponse("/admin/users", status_code=303)



@app.get("/admin/logins", response_class=HTMLResponse)
def admin_logins_view(request: Request):
    auth = require_auth(request)

    # tylko admin może przeglądać metadane logowań
    if not auth or auth.get("role") != "admin":
        return RedirectResponse(url="/login")

    db: Session = SessionLocal()
    logins = db.query(LoginMetadata).order_by(LoginMetadata.created_at.desc()).all()
    db.close()

    return templates.TemplateResponse(
        "admin_logins.html",
        {
            "request": request,
            "logins": logins
        }
    )


@app.get("/admin/cars", response_class=HTMLResponse)
def admin_cars_view(request: Request):
    auth = require_auth(request)
    if not auth or auth.get("role") != "admin":
        return RedirectResponse(url="/login")

    db: Session = SessionLocal()

    # Pobieramy wszystkie samochody
    cars = db.query(Car).options(joinedload(Car.images)).all()

    # Pobieramy mapę user_id -> username
    user_ids = [car.user_id for car in cars]
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    user_map = {user.id: user.username for user in users}

    db.close()

    return templates.TemplateResponse(
        "cars_admin.html",
        {
            "request": request,
            "cars": cars,
            "user_map": user_map  # do odczytu właściciela w szablonie
        }
    )

@app.get("/admin/car/delete/{car_id}")
def admin_delete_car(request: Request, car_id: int):
    auth = require_auth(request)
    if not auth or auth.get("role") != "admin":
        return RedirectResponse(url="/login")

    db: Session = SessionLocal()
    try:
        car = db.query(Car).filter(Car.id == car_id).first()
        if not car:
            raise HTTPException(status_code=404, detail="Ogłoszenie nie istnieje")

        # Usuń zdjęcia z dysku
        car_dir = os.path.join(UPLOAD_DIR, f"car_{car.id}")
        if os.path.exists(car_dir):
            shutil.rmtree(car_dir)

        # Usuń powiązane CarImage z bazy
        db.query(CarImage).filter(CarImage.car_id == car.id).delete()

        # Usuń auto z bazy
        db.delete(car)
        db.commit()

    finally:
        db.close()

    return RedirectResponse(url="/admin/cars", status_code=303)

@app.get("/seller", response_class=HTMLResponse)
def seller_dashboard(request: Request):
    auth = require_auth(request)
    if not auth or auth["role"] != "seller":
        return RedirectResponse("/login", status_code=303)

    db = SessionLocal()
    user = db.query(User).filter(User.username == auth["user"]).first()

    cars = (
        db.query(Car)
        .options(joinedload(Car.images))
        .filter(Car.user_id == user.id)
        .all()
    )

    db.close()

    return templates.TemplateResponse(
        "seller_dashboard.html",
        {
            "request": request,
            "user": user,
            "cars": cars
        }
    )

@app.get("/", response_class=HTMLResponse)
def welcome_view(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})

@app.get("/cars", response_class=HTMLResponse)
def cars_view(request: Request):
    auth = require_auth(request)  # może być None
    db: Session = SessionLocal()

    cars = db.query(Car).options(joinedload(Car.images)).all()
    current_user_id = None
    role = None  # <-- dodajemy domyślnie

    if auth:
        user = db.query(User).filter(User.username == auth["user"]).first()
        if user:
            current_user_id = user.id
        role = auth.get("role")  # <-- bezpiecznie, nawet jeśli auth jest None

    db.close()

    return templates.TemplateResponse(
        "cars.html",
        {
            "request": request,
            "cars": cars,
            "current_user_id": current_user_id,
            "is_logged": auth is not None,  # True/False
            "role": role
        }
    )


#-----------------------------
#----Dodawanie aut------------
#-----------------------------

@app.get("/seller/car/add", response_class=HTMLResponse)
def seller_add_car_view(request: Request):
    auth = require_auth(request)

    if not auth:
        return RedirectResponse(url="/")

    if auth["role"] != "seller":
        return templates.TemplateResponse(
            "forbidden.html",
            {
                "request": request,
                "message": "Brak uprawnień do dodawania ogłoszeń."
            }
        )

    return templates.TemplateResponse(
        "seller_add_car.html",
        {
            "request": request,
            "user": auth["user"]
        }
    )



UPLOAD_DIR = "static/uploads"  # np. katalog na zdjęcia
@app.post("/seller/car/add")
def seller_add_car(
    request: Request,
    title: str = Form(...),
    price: int = Form(...),
    year: int = Form(...),
    mileage: int = Form(...),
    brand: str = Form(...),
    model: str = Form(...),
    fuel: str = Form(...),
    engine: str = Form(...),
    description: str = Form(...),
    images: List[UploadFile] = File(default=[])  # <- opcjonalne, lista
):
    auth = require_auth(request)
    if not auth:
        return RedirectResponse(url="/")

    if auth["role"] != "seller":
        raise HTTPException(status_code=403)

    if len(images) > 50:
        raise HTTPException(status_code=400, detail="Maksymalnie 50 zdjęć")

    db = SessionLocal()
    user = db.query(User).filter(User.username == auth["user"]).first()
    if not user:
        db.close()
        raise HTTPException(status_code=404)

    car = Car(
        title=title,
        price=price,
        year=year,
        mileage=mileage,
        brand=brand,
        model=model,
        fuel=fuel,
        engine=engine,
        description=description,
        user_id=user.id
    )

    db.add(car)
    db.commit()
    db.refresh(car)

    car_id = car.id
    car_dir = os.path.join(UPLOAD_DIR, f"car_{car_id}")
    os.makedirs(car_dir, exist_ok=True)

    # zapis zdjęć tylko jeśli są faktycznie przesłane
    for idx, image in enumerate(images):
        if image.filename:  # <-- ignoruje puste pliki
            image.file.seek(0)
            filename = f"{idx+1}_{os.path.basename(image.filename)}"
            path = os.path.join(car_dir, filename)

            with open(path, "wb") as f:
                f.write(image.file.read())

            db.add(
                CarImage(
                    car_id=car_id,
                    filename=f"car_{car_id}/{filename}",
                    is_main=(idx == 0)
                )
            )

    db.commit()
    db.close()

    return RedirectResponse(url=f"/car/{car_id}", status_code=303)


@app.get("/car/{car_id}")
def car_view(car_id: int, request: Request):
    db = SessionLocal()
    car = db.query(Car).options(joinedload(Car.images)).filter(Car.id == car_id).first()
    db.close()
    if not car:
        raise HTTPException(status_code=404, detail="Samochód nie znaleziony")
    return templates.TemplateResponse("car.html", {"request": request, "car": car})


@app.get("/seller/car/{car_id}/edit/")
def seller_edit_car_view(request: Request, car_id: int):
    auth = require_auth(request)
    if not auth or auth["role"] != "seller":
        return RedirectResponse(url="/")

    db: Session = SessionLocal()
    # Pobieramy użytkownika
    user = db.query(User).filter(User.username == auth["user"]).first()
    if not user:
        db.close()
        return RedirectResponse(url="/login")

    # Pobieramy samochód razem z obrazkami (joinedload)
    car = db.query(Car).options(joinedload(Car.images)).filter(Car.id == car_id).first()

    # Sprawdzamy, czy samochód należy do aktualnego użytkownika
    if not car or car.user_id != user.id:
        db.close()
        raise HTTPException(status_code=404, detail="Brak ogłoszenia lub brak uprawnień")

    db.close()

    return templates.TemplateResponse(
        "seller_car_edit.html",
        {"request": request, "car": car}
    )

from PIL import Image, UnidentifiedImageError
from io import BytesIO
import shutil


@app.post("/seller/car/{car_id}/edit/")
def seller_edit_car(
        request: Request,
        car_id: int,
        title: str = Form(...),
        price: int = Form(...),
        year: int = Form(...),
        mileage: int = Form(...),
        brand: str = Form(...),
        model: str = Form(...),
        fuel: str = Form(...),
        engine: str = Form(...),
        description: str = Form(...),
        images: list[UploadFile] = File([])  # nowe zdjęcia
):
    auth = require_auth(request)
    if not auth or auth["role"] != "seller":
        return RedirectResponse(url="/")

    db = SessionLocal()
    try:
        car = db.query(Car).filter(Car.id == car_id).first()
        if not car:
            raise HTTPException(status_code=404)

        user = db.query(User).filter(User.username == auth["user"]).first()
        if not user or car.user_id != user.id:
            raise HTTPException(status_code=403)

        # --- Aktualizacja pól ---
        car.title = title
        car.price = price
        car.year = year
        car.mileage = mileage
        car.brand = brand
        car.model = model
        car.fuel = fuel
        car.engine = engine
        car.description = description

        db.add(car)
        db.commit()
        db.refresh(car)

        car_id_to_redirect = car.id  # ✅ przed zamknięciem sesji

        # --- Obsługa nowych zdjęć ---
        if images:
            car_dir = os.path.join(UPLOAD_DIR, f"car_{car.id}")
            os.makedirs(car_dir, exist_ok=True)

            existing_images = db.query(CarImage).filter(CarImage.car_id == car.id).all()
            has_main = any(img.is_main for img in existing_images)
            current_image_count = len(existing_images)

            for idx, image in enumerate(images):
                image.file.seek(0)
                content = image.file.read()

                if len(content) == 0:
                    continue  # <-- ignorujemy puste pliki

                original_filename = os.path.basename(image.filename)
                filename = f"{current_image_count + idx + 1}_{original_filename}"
                path = os.path.join(car_dir, filename)

                # zapis pliku
                with open(path, "wb") as f:
                    f.write(content)

                db.add(
                    CarImage(
                        car_id=car.id,
                        filename=f"car_{car.id}/{filename}",
                        is_main=(not has_main and idx == 0)
                    )
                )

            db.commit()

    finally:
        db.close()

    return RedirectResponse(url=f"/car/{car_id_to_redirect}", status_code=303)


@app.get("/seller/car/delete/{car_id}")
def seller_delete_car(request: Request, car_id: int):
    auth = require_auth(request)
    if not auth:
        return RedirectResponse(url="/")

    if auth["role"] != "seller":
        raise HTTPException(status_code=403)

    db: Session = SessionLocal()
    try:
        car = db.query(Car).filter(Car.id == car_id).first()
        if not car:
            raise HTTPException(status_code=404, detail="Ogłoszenie nie istnieje")

        user = db.query(User).filter(User.username == auth["user"]).first()
        if not user or car.user_id != user.id:
            raise HTTPException(status_code=403, detail="Brak uprawnień")

        # Usuń zdjęcia z dysku
        car_dir = os.path.join(UPLOAD_DIR, f"car_{car.id}")
        if os.path.exists(car_dir):
            shutil.rmtree(car_dir)

        # Usuń powiązane CarImage z bazy
        db.query(CarImage).filter(CarImage.car_id == car.id).delete()

        # Usuń auto z bazy
        db.delete(car)
        db.commit()

    finally:
        db.close()

    return RedirectResponse(url="/cars", status_code=303)















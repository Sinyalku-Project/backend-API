from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import requests
import time

from app.database import get_db
from app.models import SignalReading as SignalReadingModel, User as UserModel
from app.schemas import (
    SignalReadingCreate,
    SignalReading as SignalReadingSchema,
    UserCreate,
    User as UserSchema,
    Token,
)
from app.auth import authenticate_user, create_access_token, get_current_active_user, get_password_hash
from sqlalchemy.orm import Session

app = FastAPI(title="SinyalKu API (revised)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory cache for Nominatim responses
_GEO_CACHE: dict = {}
_CACHE_TTL = 60 * 60 * 24  # 24 hours


@app.get("/")
def root():
    return {"message": "SinyalKu backend API is running!"}


@app.post("/register", response_model=UserSchema)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check existing user
    existing = db.query(UserModel).filter(
        (UserModel.username == user.username) |
        (UserModel.email == user.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # Create new user
    hashed_pw = get_password_hash(user.password)
    new_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=Token)
def token_endpoint(form_data: dict, db=Depends(get_db)):
    user = authenticate_user(db, form_data.get("username"), form_data.get("password"))
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# ✅ Reverse geocoding helper
def reverse_geocode_country(lat: float, lon: float) -> Optional[str]:
    now = time.time()
    cache_key = f"{lat:.4f},{lon:.4f}"
    cached = _GEO_CACHE.get(cache_key)
    if cached and now - cached["ts"] < _CACHE_TTL:
        return cached["data"]

    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": lat, "lon": lon, "format": "json"}
    headers = {"User-Agent": "SinyalKu/1.0 (contact@example.com)"}  # replace contact

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=12)
        if resp.status_code == 429:
            raise HTTPException(status_code=429, detail="Nominatim rate limit exceeded")
        resp.raise_for_status()
        data = resp.json()
        country = data.get("address", {}).get("country")
        _GEO_CACHE[cache_key] = {"ts": now, "data": country}
        return country
    except requests.RequestException:
        return None

@app.post("/api/readings/", response_model=SignalReadingSchema)
def create_reading(
    reading: SignalReadingCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db=Depends(get_db),
):
    # ✅ If country is missing, get it from lat/lon
    country_name = reading.country
    if not country_name:
        country_name = reverse_geocode_country(reading.latitude, reading.longitude)

    db_r = SignalReadingModel(
        latitude=reading.latitude,
        longitude=reading.longitude,
        signal_strength=reading.signal_strength,
        operator=reading.operator,
        country=country_name,
        user_id=current_user.id,
    )
    db.add(db_r)
    db.commit()
    db.refresh(db_r)
    return db_r


@app.get("/api/readings/", response_model=List[SignalReadingSchema])
def get_readings(
    min_lat: Optional[float] = None,
    max_lat: Optional[float] = None,
    min_lon: Optional[float] = None,
    max_lon: Optional[float] = None,
    operator: Optional[str] = None,
    country: Optional[str] = None,
    db=Depends(get_db),
):
    query = db.query(SignalReadingModel)
    if None not in (min_lat, max_lat, min_lon, max_lon):
        query = query.filter(
            SignalReadingModel.latitude >= min_lat,
            SignalReadingModel.latitude <= max_lat,
            SignalReadingModel.longitude >= min_lon,
            SignalReadingModel.longitude <= max_lon,
        )
    if operator:
        query = query.filter(SignalReadingModel.operator == operator)
    if country:
        query = query.filter(SignalReadingModel.country == country)
    return query.all()


@app.get("/api/readings/best", response_model=Optional[SignalReadingSchema])
def get_best(
    min_lat: Optional[float] = None,
    max_lat: Optional[float] = None,
    min_lon: Optional[float] = None,
    max_lon: Optional[float] = None,
    operator: Optional[str] = None,
    country: Optional[str] = None,
    db=Depends(get_db),
):
    query = db.query(SignalReadingModel)
    if None not in (min_lat, max_lat, min_lon, max_lon):
        query = query.filter(
            SignalReadingModel.latitude >= min_lat,
            SignalReadingModel.latitude <= max_lat,
            SignalReadingModel.longitude >= min_lon,
            SignalReadingModel.longitude <= max_lon,
        )
    if operator:
        query = query.filter(SignalReadingModel.operator == operator)
    if country:
        query = query.filter(SignalReadingModel.country == country)
    best = query.order_by(SignalReadingModel.signal_strength.desc()).limit(1).all()
    return best[0] if best else None


@app.get("/api/operators/", response_model=List[str])
def operators(db=Depends(get_db)):
    rows = db.query(SignalReadingModel.operator).distinct().all()
    return [r[0] for r in rows if r[0]]


@app.get("/api/countries/", response_model=List[str])
def countries(db=Depends(get_db)):
    rows = db.query(SignalReadingModel.country).distinct().all()
    return [r[0] for r in rows if r[0]]


@app.get("/api/geocode-country/")
def geocode_country(country: str = Query(..., min_length=1)):
    """
    Proxy to Nominatim with server-side caching and proper headers.
    Returns the raw Nominatim JSON array (first result usually contains geojson).
    """
    now = time.time()
    cached = _GEO_CACHE.get(country)
    if cached and now - cached["ts"] < _CACHE_TTL:
        return cached["data"]

    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": country, "format": "json", "polygon_geojson": 1, "limit": 3}
    headers = {"User-Agent": "SinyalKu/1.0 (contact@example.com)"}  # replace contact

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=12)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Nominatim request failed: {str(e)}")

    if resp.status_code == 429:
        raise HTTPException(status_code=429, detail="Nominatim rate limit exceeded")
    if not resp.ok:
        raise HTTPException(status_code=resp.status_code, detail=f"Nominatim returned {resp.status_code}")

    try:
        data = resp.json()
    except ValueError:
        raise HTTPException(status_code=502, detail="Invalid JSON from Nominatim")

    _GEO_CACHE[country] = {"ts": now, "data": data}
    return data

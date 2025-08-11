# SinyalKu Backend - FastAPI + PostGIS

FastAPI backend for the **SinyalKu** crowdsourced network quality monitoring platform, featuring JWT authentication and PostGIS geospatial support.

---

## Project Structure
```
backend-API/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application & endpoints
│   ├── models.py            # SQLAlchemy models (User, SignalReading)
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # JWT authentication utilities
│   └── database.py          # Database connection setup
└── requirements.txt         # Python dependencies
```

---

## Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/Sinyalku-Project/backend-API.git
cd backend-API
```

---

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

### 3. Database Setup

#### Create PostgreSQL Database with PostGIS
```bash
createdb sinyalku_db
psql -d sinyalku_db -c "CREATE EXTENSION postgis;"
```

#### Initialize Alembic (first time only)
```bash
alembic init alembic
```

#### Configure Alembic to Detect Models
Edit `alembic/env.py` and add:
```python
from app import models
target_metadata = models.Base.metadata
```

#### Run Database Migrations
```bash
alembic upgrade head
```

---

### 4. Environment Variables
Create a `.env` file in the `backend-API/` directory:
```env
DATABASE_URL=postgresql://<user>:<password>@localhost/sinyalku_db
SECRET_KEY=your-secret-key-here
```

---

### 5. Run Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## API Endpoints Overview

### Authentication
- `POST /token` → Generate JWT access token

### Signal Readings
- `POST /api/readings/` → Submit a new signal reading (**auth required**)
- `GET /api/readings/` → Retrieve readings with optional filters (bounding box, operator, country)
- `GET /api/readings/best` → Get best signal reading based on filters
- `GET /api/operators/` → List available operators
- `GET /api/countries/` → List available countries
- `GET /api/geocode-country/` → Get geospatial data for a country (via Nominatim API)

---

## Database Models

### **User**
- `id`: Integer (Primary Key)
- `username`: String (Unique)
- `email`: String (Unique)
- `hashed_password`: String
- `is_active`: Boolean
- `created_at`: DateTime
- `points`: Integer
- `rank`: String

### **SignalReading**
- `id`: Integer (Primary Key)
- `latitude`: Float
- `longitude`: Float
- `signal_strength`: Float
- `operator`: String
- `country`: String (Optional)
- `timestamp`: DateTime
- `user_id`: Integer (Foreign Key → User)
- `geom`: Geometry(Point, SRID=4326)

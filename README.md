# SinyalKu Backend - FastAPI + PostGIS

FastAPI backend for SinyalKu crowdsourced network quality monitoring platform with JWT authentication and PostGIS geospatial support.

## Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application & endpoints
│   ├── models.py        # SQLAlchemy models (User, SignalReading)
│   ├── schemas.py       # Pydantic schemas
│   ├── auth.py          # JWT authentication utilities
│   └── database.py      # Database connection setup
├── requirements.txt     # Python dependencies
└── alembic.ini         # Database migrations
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Create PostgreSQL database with PostGIS
createdb sinyalku_db

# Run migrations
alembic upgrade head
```

### 3. Environment Variables
Create `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost/sinyalku_db
SECRET_KEY=your-secret-key-here
```

### 4. Run Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /token` - JWT token generation
- `GET /users/me/` - Get current user info

### Data
- `POST /api/readings/` - Submit signal reading (auth required)
- `GET /api/readings/` - Get readings with bounding box and operator filter
- `GET /api/operators/` - Get unique operators list
- `GET /api/stats/` - Dashboard statistics

## Database Models
- **User**: id, username, email, hashed_password, points, rank
- **SignalReading**: id, latitude, longitude, signal_strength, operator, user_id, geom

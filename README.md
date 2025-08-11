# SinyalKu Backend

FastAPI backend for the **SinyalKu** crowdsourced network quality monitoring platform, featuring JWT authentication and PostGIS geospatial support.

---

## Project Overview

This backend API handles user authentication, submission, and querying of signal quality data with geospatial capabilities using PostGIS.

---

## Project Structure

```
backend-API/
├── alembic/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app and endpoints
│   ├── models.py            # SQLAlchemy models (User, SignalReading)
│   ├── schemas.py           # Pydantic schemas for data validation
│   ├── auth.py              # JWT authentication utilities
│   └── database.py          # Database connection and setup
├── requirements.txt         # Python dependencies
└── alembic.ini              # Alembic configuration file
```

---

## Setup and Deployment Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/Sinyalku-Project/backend-API.git
cd backend-API
```

---

### Step 2: Install Dependencies

Ensure you have Python 3.9+ installed, then run:

```bash
pip install -r requirements.txt
```

---

### Step 3: Setup Database with PostGIS

1. Log in to your Supabase dashboard or your PostgreSQL server.
2. Run the following SQL command to enable PostGIS extension:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

---

### Step 4: Configure Alembic for Database Migrations

If Alembic is not initialized yet, run:

```bash
alembic init alembic
```

Edit `alembic/env.py` and add the following to detect your SQLAlchemy models:

```python
from app import models
target_metadata = models.Base.metadata
```

Run the migrations to create database tables:

```bash
alembic upgrade head
```

---

### Step 5: Configure Environment Variables

Create a `.env` file in the project root with the following variables:

```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-ID].supabase.co:5432/postgres
SECRET_KEY=[your-secret-key]
```

Replace placeholders with your actual database credentials and a strong secret key for JWT.

---

### Step 6: Run the Application Locally (Optional)

Start the FastAPI server locally for development/testing:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open your browser and visit: `http://localhost:8000`

---

### Step 7: Deploy to Render

1. Create a new web service on [Render](https://render.com).
2. Connect your GitHub repository (`backend-API`).
3. Set the **Build Command** to:

```bash
pip install -r requirements.txt
```

4. Set the **Start Command** to:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

5. Add environment variables in Render's dashboard (`DATABASE_URL`, `SECRET_KEY`, etc.).
6. Deploy the service and wait for it to be live.

---

## API Endpoints Overview

- **Authentication**
  - `POST /token` : Generate JWT access token.

- **Signal Readings**
  - `POST /api/readings/` : Submit new signal reading (requires authentication).
  - `GET /api/readings/` : Retrieve signal readings with optional filters (bounding box, operator, country).
  - `GET /api/readings/best` : Retrieve the best signal reading based on filters.
  - `GET /api/operators/` : List available operators.
  - `GET /api/countries/` : List available countries.
  - `GET /api/geocode-country/` : Get geospatial data for a country (via Nominatim API).

---

## Database Models Summary

### User

| Field           | Type       | Description                  |
|-----------------|------------|------------------------------|
| id              | Integer    | Primary Key                  |
| username        | String     | Unique                      |
| email           | String     | Unique                      |
| hashed_password | String     | Password hash               |
| is_active       | Boolean    | User active status          |
| created_at      | DateTime   | Account creation timestamp  |
| points          | Integer    | User points for gamification|
| rank            | String     | User rank                   |

### SignalReading

| Field           | Type          | Description                  |
|-----------------|---------------|------------------------------|
| id              | Integer       | Primary Key                  |
| latitude        | Float         | Latitude coordinate          |
| longitude       | Float         | Longitude coordinate         |
| signal_strength | Float         | Signal strength value (dBm) |
| operator        | String        | Network operator             |
| country         | String (opt.) | Country name                 |
| timestamp       | DateTime      | Reading timestamp            |
| user_id         | Integer       | Foreign key to User          |
| geom            | Geometry(Point, SRID=4326) | Geospatial point        |

---

## Notes

- This project is still under active development.
- Feel free to contribute or raise issues on the GitHub repository.

---

If you need help or have questions, open an issue or contact the maintainer.

---

**Happy coding! 🚀**

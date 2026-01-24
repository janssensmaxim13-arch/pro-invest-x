# ProInvestiX Enterprise API

Backend API for the ProInvestiX National Investment Platform.

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLAlchemy (async) + SQLite/PostgreSQL
- **Auth**: JWT (python-jose) + bcrypt
- **Validation**: Pydantic v2

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
```

### 3. Run Development Server

```bash
# Run with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python -m app.main
```

### 4. Access API

- **API**: http://localhost:8000
- **Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
proinvestix-api/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings
│   ├── core/
│   │   ├── security.py      # JWT & password hashing
│   │   ├── dependencies.py  # FastAPI dependencies
│   │   └── exceptions.py    # Custom exceptions
│   ├── db/
│   │   ├── database.py      # Database connection
│   │   └── models.py        # SQLAlchemy models (43)
│   ├── schemas/
│   │   └── auth.py          # Pydantic schemas
│   ├── api/v1/
│   │   ├── router.py        # Main API router
│   │   └── endpoints/
│   │       └── auth.py      # Auth endpoints
│   ├── services/            # Business logic
│   └── utils/               # Helpers
├── tests/                   # Test files
├── alembic/                 # Migrations
├── requirements.txt
├── .env.example
└── README.md
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/register` | Register |
| POST | `/api/v1/auth/refresh` | Refresh token |
| GET | `/api/v1/auth/me` | Get current user |
| POST | `/api/v1/auth/change-password` | Change password |
| POST | `/api/v1/auth/logout` | Logout |

### More endpoints coming soon...

## Default Admin Account

- **Email**: admin@proinvestix.ma
- **Password**: admin123
- **Role**: SuperAdmin

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `false` |
| `DATABASE_URL` | Database connection | SQLite |
| `SECRET_KEY` | JWT secret key | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | `30` |
| `CORS_ORIGINS` | Allowed origins | `localhost` |

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## Production Deployment

### Railway

1. Create new project on Railway
2. Connect GitHub repository
3. Set environment variables
4. Deploy!

### Docker

```bash
# Build image
docker build -t proinvestix-api .

# Run container
docker run -p 8000:8000 proinvestix-api
```

## License

Proprietary - ProInvestiX

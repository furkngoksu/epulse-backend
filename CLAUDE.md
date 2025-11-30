# E-Pulse Backend

## Project Overview
E-Pulse is a health application backend with medication tracking and doctor appointment features. This is the API server that powers the E-Pulse mobile healthcare system.

## Technology Stack

### Package & Project Management
- **uv**: Python package and project manager
- **Python**: >=3.11 (specified in `.python-version`)

### Core Framework
- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running the application
- **Pydantic**: Data validation using Python type annotations
- **SQLAlchemy**: SQL toolkit and ORM for database operations

### Database
- **PostgreSQL**: Primary database (via psycopg2-binary)
- Connection configured through `DATABASE_URL` environment variable

### Authentication & Security
- **JWT (JSON Web Tokens)**: Token-based authentication
- **python-jose**: JWT token implementation
- **Passlib**: Password hashing
- **Bcrypt**: Password hashing algorithm
- Access tokens expire in 60 minutes
- Refresh tokens expire in 30 days

## Project Structure

```
epulse-backend/
    app/
        api/           # API routes and endpoints
            v1/        # API version 1 routes
                auth.py    # Authentication endpoints
            deps/      # Dependency injection modules
                 auth.py    # Auth dependencies
                 db.py      # Database dependencies
        core/          # Core application configuration
            config.py      # Settings and environment variables
            security.py    # Security utilities (JWT, hashing)
        db/            # Database configuration
            base.py        # Base models
            session.py     # Database session management
            init_db.py     # Database initialization
        models/        # SQLAlchemy database models
            user.py        # User model
        schemas/       # Pydantic schemas for validation
            auth.py        # Authentication schemas
            user.py        # User schemas
        repositories/  # Database access layer
            user.py        # User repository
        services/      # Business logic layer
            user.py        # User service
        exceptions/    # Custom exceptions
        utils/         # Utility functions
        main.py        # Application entry point
    pyproject.toml     # Project configuration and dependencies
    requirements.txt   # Python dependencies
    .env              # Environment variables (not in git)
```

## Architecture Pattern

The project follows a layered architecture:

1. **API Layer** (`api/`): FastAPI route handlers
2. **Service Layer** (`services/`): Business logic
3. **Repository Layer** (`repositories/`): Database access abstraction
4. **Model Layer** (`models/`): SQLAlchemy ORM models
5. **Schema Layer** (`schemas/`): Pydantic models for validation and serialization

## Configuration

Environment variables (defined in `.env`):
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret key for access tokens
- `JWT_REFRESH_SECRET_KEY`: Secret key for refresh tokens
- `JWT_ALGORITHM`: Algorithm for JWT (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token expiration (default: 60)
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration (default: 30)

## Running the Application

The application runs on:
- **Host**: 127.0.0.1
- **Port**: 8000
- **Reload**: Enabled in development

Start with: `python -m app.main` or `uvicorn app.main:app --reload`

## API Information

- **Title**: E-Pulse Mobile API
- **Description**: Backend API for E-Pulse mobile healthcare system
- **Version**: 1.0.0
- **API Prefix**: `/api/v1` (from router configuration)

## Error Handling

The application uses custom error handling:
- HTTPException returns: `{"success": false, "error": "<detail>"}`
- Validation errors return: `{"success": false, "error": {"code": "VALIDATION_ERROR", "fields": [...]}}`

## Development Notes

- Database initialization happens during application startup via `lifespan` context manager
- All responses follow a consistent format with `success` and `error` fields
- The project uses dependency injection for database sessions and authentication
- Current features include user authentication (login/register)

## Key Dependencies

- `fastapi>=0.121.2`: Web framework
- `sqlalchemy>=2.0.44`: ORM
- `pydantic>=2.12.4`: Data validation
- `python-jose[cryptography]>=3.5.0`: JWT handling
- `bcrypt>=4.0.0`: Password hashing
- `psycopg2-binary>=2.9.11`: PostgreSQL adapter
- `uvicorn>=0.38.0`: ASGI server
- `email-validator>=2.3.0`: Email validation

# ePulse Backend

FastAPI backend for ePulse, a mobile healthcare prototype built as a team project at Istanbul Technical University. Patients can book appointments, view prescriptions, and track medication doses. The backend also provides doctor profiles, medication adherence reports, and a chat assistant.

[Original team repository](https://github.com/ITU-Core-Dumped/epulse-backend) · [Mobile client](https://github.com/ITU-Core-Dumped/epulse-frontend-mobile)

## Architecture

The API is versioned under `/api/v1`. Routes in `app/api/v1/` call services in `app/services/`, with SQLAlchemy repositories and models handling PostgreSQL persistence. Pydantic schemas define the request and response formats.

## Local development

Use Python 3.11 or later, uv, and a local PostgreSQL database. From the repository root, create a `.env` file with `DATABASE_URL` and two distinct local secrets for `JWT_SECRET_KEY` and `JWT_REFRESH_SECRET_KEY`.

```bash
uv sync
uv run uvicorn app.main:app --reload
```

The app creates database tables at startup. Swagger UI is available at [localhost:8000/docs](http://localhost:8000/docs).

The chat assistant requires `OPENAI_API_KEY` and `OPENAI_ASSISTANT_ID`. Email delivery requires `MAILEROO_API_KEY`. Use synthetic records when trying the app locally. The team's private documentation is separate from the public backend.

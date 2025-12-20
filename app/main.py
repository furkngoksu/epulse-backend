from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.db.init_db import init_db
from app.api.v1 import app_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database - create tables if they don't exist
    init_db()
    print("📌 Database initialized - tables created if not exists.")
    yield
    # Shutdown
    print("👋 Application shutting down...")


app = FastAPI(
    lifespan=lifespan,
    title="E-Pulse Mobile API",
    description="Backend API for E-Pulse mobile healthcare system.",
    version="1.0.0"
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "fields": exc.errors()
            }
        }
    )

app.include_router(app_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,        
        log_level="info"
    )

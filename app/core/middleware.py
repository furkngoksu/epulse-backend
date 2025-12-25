import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.log_context import request_id_var, user_id_var

logger = logging.getLogger("request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        request_id_var.set(rid)
        user_id_var.set("-")

        start = time.perf_counter()
        try:
            response = await call_next(request)
            duration_ms = int((time.perf_counter() - start) * 1000)

            logger.info(
                f"{request.method} {request.url.path} {response.status_code} {duration_ms}ms"
            )

            response.headers["X-Request-Id"] = rid
            return response
        except Exception:
            logger.exception(f"Error: {request.method} {request.url.path}")
            raise

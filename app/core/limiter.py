from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.security import get_user_id_from_token


def _user_or_ip_key(request: Request) -> str:
    """
    Rate limit key function: prefer user_id from JWT, otherwise fall back to client IP.
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        try:
            return str(get_user_id_from_token(token))
        except Exception:
            # Fall back to IP on invalid/expired tokens to avoid 500s.
            pass

    return get_remote_address(request)


limiter = Limiter(key_func=_user_or_ip_key)

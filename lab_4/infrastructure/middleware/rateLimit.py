from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from datetime import datetime, timedelta
from collections import defaultdict


# Initialize limiter - shared instance
limiter = Limiter(key_func=get_remote_address)

# In-memory storage for rate limiting (simple implementation)
# In production, use Redis or similar
_rate_limit_storage = defaultdict(list)

class GlobalRateLimitMiddleware(BaseHTTPMiddleware):
    """Global rate limiter - 50 requests per 15 minutes"""
    
    async def dispatch(self, request: Request, call_next):

        # Skip rate limiting for docs and static files only
        if request.url.path.startswith(("/docs", "/openapi.json", "/redoc", "/favicon.ico")):
            return await call_next(request)

        # Get client identifier
        identifier = get_remote_address(request)
        current_time = datetime.now()
        window_start = current_time - timedelta(minutes=15)

        # Clean old entries
        if identifier in _rate_limit_storage:
            _rate_limit_storage[identifier] = [
                ts for ts in _rate_limit_storage[identifier]
                if ts > window_start
            ]

        # Check limit
        request_count = len(_rate_limit_storage[identifier])

        # Call next middleware/endpoint
        response = await call_next(request)

        # If a previous middleware returned 413, do not count or rate limit
        if getattr(response, 'status_code', None) == 413:
            return response

        if request_count >= 50:
            reset_time = current_time + timedelta(minutes=15)
            response = JSONResponse(
                status_code=429,
                content={"error": "Zbyt wiele requestow. Sprobuj ponownie za 15 minut."},
                headers={
                    "Retry-After": "900",
                    "RateLimit-Limit": "50",
                    "RateLimit-Remaining": "0",
                    "RateLimit-Reset": str(int(reset_time.timestamp()))
                }
            )
            return response

        # Record this request (only if not 413)
        _rate_limit_storage[identifier].append(current_time)

        # Add rate limit headers
        remaining = 50 - request_count - 1
        reset_time = current_time + timedelta(minutes=15)

        response.headers["RateLimit-Limit"] = "50"
        response.headers["RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["RateLimit-Reset"] = str(int(reset_time.timestamp()))

        return response

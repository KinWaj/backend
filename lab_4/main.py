
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse

# Middleware to limit total header size (e.g., 16KB)
class HeaderSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        max_header_size = 16 * 1024  # 16KB
        total_size = sum(len(k) + len(v) for k, v in request.headers.items())
        if total_size > max_header_size:
            return JSONResponse(status_code=431, content={"error": "Request Header Fields Too Large"})
        return await call_next(request)

# Middleware to limit request body size (e.g., 1MB)
class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        from starlette.requests import ClientDisconnect
        max_body_size = 1024 * 1024  # 1MB
        body = None
        if request.method in ("POST", "PUT", "PATCH"):  # Only read body for these methods
            try:
                body = await request.body()
            except ClientDisconnect:
                body = None
        if body is not None and len(body) > max_body_size:
            return JSONResponse(status_code=413, content={"error": "Payload Too Large"})
        return await call_next(request)
from dotenv import load_dotenv
load_dotenv()

from infrastructure.monitoring.sentry import init_sentry
# Initialize Sentry before anything else
init_sentry()

from fastapi import FastAPI, Request

from fastapi.responses import Response, JSONResponse

from starlette.middleware.base import BaseHTTPMiddleware

from slowapi.errors import RateLimitExceeded
from infrastructure.middleware.rateLimit import limiter, GlobalRateLimitMiddleware
from routes import tasks, admin
from routes import last_lessons_endpoints
from auth import router as auth_router
import logging
import sentry_sdk

class HelmetMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Security headers equivalent to Helmet.js
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "0"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response


app = FastAPI(title='Todo API')
app.state.limiter = limiter

# ============================================
# EXCEPTION HANDLERS (before middleware)
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global error handler - Sentry captures errors before this runs"""
    import traceback
    logging.error(f"Unhandled exception: {exc}")
    logging.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limiting"""
    from datetime import datetime, timedelta
    
    # Optionally capture rate limit events in Sentry
    sentry_sdk.capture_message(
        f"Rate limit exceeded for {request.url.path}",
        level="warning",
        extras={"path": request.url.path, "client": request.client.host if request.client else "unknown"}
    )
    
    if request.url.path.startswith("/auth"):
        reset_time = datetime.now() + timedelta(minutes=1)
        return JSONResponse(
            status_code=429,
            content={"error": "Zbyt wiele prob logowania. Poczekaj minute."},
            headers={
                "Retry-After": "60",
                "RateLimit-Limit": "5",
                "RateLimit-Remaining": "0",
                "RateLimit-Reset": str(int(reset_time.timestamp()))
            }
        )
    else:
        reset_time = datetime.now() + timedelta(minutes=15)
        return JSONResponse(
            status_code=429,
            content={"error": "Zbyt wiele requestow. Sprobuj ponownie za 15 minut."},
            headers={
                "Retry-After": "900",
                "RateLimit-Limit": "100",
                "RateLimit-Remaining": "0",
                "RateLimit-Reset": str(int(reset_time.timestamp()))
            }
        )

# ============================================
# MIDDLEWARE (order matters!)
# ============================================

# CORS optional for frontend development in the future :)
#app.add_middleware(
#    CORSMiddleware,
#    allow_origins=["http://localhost:8000"],
#    allow_credentials=True,
#    allow_methods=["*"],
#    allow_headers=["*"],
#)


app.add_middleware(HeaderSizeLimitMiddleware)
app.add_middleware(BodySizeLimitMiddleware)
app.add_middleware(HelmetMiddleware)
from slowapi.middleware import SlowAPIMiddleware
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(GlobalRateLimitMiddleware)

# ============================================
# CONFIGURE LOGGING
# ============================================

logging.getLogger("uvicorn.access").addFilter(
    lambda record: "/favicon.ico" not in record.getMessage()
)

# ============================================
# ROUTES
# ============================================

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return Response(status_code=204)

#@app.get('/debug-sentry')
#async def debug_sentry():
#    """Test endpoint to verify Sentry is working"""
#    raise Exception('Testowy blad Sentry!')

# Include routers
app.include_router(auth_router)
app.include_router(tasks.router)
app.include_router(last_lessons_endpoints.router)
app.include_router(admin.router)
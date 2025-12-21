from fastapi import FastAPI, Request
from fastapi.responses import Response
from routes import tasks, admin
from routes import last_lessons_endpoints
from auth import router as auth_router
import logging


app = FastAPI(title='Todo API')

logging.getLogger("uvicorn.access").addFilter(
    lambda record: "/favicon.ico" not in record.getMessage()
)


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return Response(status_code=204)


app.include_router(auth_router)
app.include_router(tasks.router)
app.include_router(last_lessons_endpoints.router)
app.include_router(admin.router)

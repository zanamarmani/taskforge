from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis import Redis
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="A reliable background job processing platform.",
    lifespan=lifespan,
)


@app.get("/", tags=["General"])
def root():
    return {
        "message": "Welcome to TaskForge",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


@app.get("/health/ready", tags=["Health"])
def readiness():
    # Return success only when both dependencies are reachable.
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    redis_client = Redis.from_url(
        settings.redis_url,
        socket_connect_timeout=2,
        socket_timeout=2,
    )

    try:
        redis_client.ping()
    finally:
        redis_client.close()

    return {
        "status": "ready",
        "database": "connected",
        "redis": "connected",
    }

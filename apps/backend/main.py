from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.repositories.token_repository import ensure_token_indexes
from auth.repositories.user_repository import ensure_user_indexes
from auth.routers.auth_router import router as auth_router
from core.database import connect_to_mongodb, disconnect_from_mongodb, get_database
from core.exceptions import register_exception_handlers
from core.settings import get_settings
from routers.health_router import router as health_router

settings = get_settings()
cors_origins = [origin.strip() for origin in settings.app_cors_origins.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await connect_to_mongodb(settings)
    database = get_database()
    await ensure_user_indexes(database)
    await ensure_token_indexes(database)
    try:
        yield
    finally:
        await disconnect_from_mongodb()


app = FastAPI(title="NexusERP Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(health_router)
app.include_router(auth_router)

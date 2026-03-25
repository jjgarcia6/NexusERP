from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.repositories.token_repository import ensure_token_indexes
from auth.repositories.user_repository import ensure_user_indexes
from auth.routers.auth_router import router as auth_router
from catalog.repositories.category_repository import ensure_category_indexes
from catalog.repositories.product_repository import ensure_product_indexes
from catalog.routers.categories_router import router as categories_router
from catalog.routers.products_router import router as products_router
from core.database import connect_to_mongodb, disconnect_from_mongodb, get_database
from core.exceptions import register_exception_handlers
from core.settings import get_settings
from purchases.repositories.purchase_order_repository import ensure_purchase_order_indexes
from purchases.repositories.supplier_repository import ensure_supplier_indexes
from purchases.routers.purchases_router import router as purchases_router
from purchases.routers.suppliers_router import router as suppliers_router
from routers.health_router import router as health_router

settings = get_settings()
cors_origins = [origin.strip() for origin in settings.app_cors_origins.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await connect_to_mongodb(settings)
    database = get_database()
    await ensure_user_indexes(database)
    await ensure_token_indexes(database)
    await ensure_category_indexes(database)
    await ensure_product_indexes(database)
    await ensure_supplier_indexes(database)
    await ensure_purchase_order_indexes(database)
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
app.include_router(categories_router, prefix="/categories", tags=["catalog"])
app.include_router(products_router, prefix="/products", tags=["catalog"])
app.include_router(suppliers_router, prefix="/suppliers", tags=["purchases"])
app.include_router(purchases_router, prefix="/purchases", tags=["purchases"])

from __future__ import annotations

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError

from core.database import get_database
from core.schemas import HealthResponse, ServiceUnavailableResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ServiceUnavailableResponse}},
)
async def get_health() -> HealthResponse | JSONResponse:
    database = get_database()
    try:
        await database.command("ping")
        return HealthResponse()
    except PyMongoError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=ServiceUnavailableResponse().model_dump(),
        )

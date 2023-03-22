from fastapi import APIRouter

from .endpoints import (
    authentication
)

api_router = APIRouter()
api_router.include_router(
    authentication.router,
    tags=["authentication"],
    prefix="/authentication",
    dependencies=[],
)

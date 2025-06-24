from fastapi import APIRouter
from .cats import router as cats_router
from .missions import router as missions_router

main_api_router = APIRouter(prefix="/api")

main_api_router.include_router(cats_router)
main_api_router.include_router(missions_router)
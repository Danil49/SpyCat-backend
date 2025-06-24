from fastapi import APIRouter
from .cats import router as cats_router

main_api_router = APIRouter(prefix="/api")

main_api_router.include_router(cats_router)
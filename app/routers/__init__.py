from fastapi import APIRouter

from .scrap import router as scrap_router


router = APIRouter()
router.include_router(scrap_router)

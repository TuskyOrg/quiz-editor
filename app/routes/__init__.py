from fastapi import APIRouter

from app.routes.editor import router as editor_router
from app.routes.room_management import router as room_management_router

router = APIRouter()

router.include_router(editor_router, prefix="/editor", tags=["editor"])
router.include_router(room_management_router, prefix="/room-management", tags=["room"])

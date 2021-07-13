from fastapi import APIRouter

from app.routes.editor import router as editor_router
from app.routes.room import router as room_router

router = APIRouter()

router.include_router(editor_router, prefix="/editor", tags=["editor"])
router.include_router(room_router, prefix="/room", tags=["room"])

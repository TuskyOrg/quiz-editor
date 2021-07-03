from fastapi import APIRouter

from app.routes.editor import router as editor_router

router = APIRouter()

router.include_router(editor_router, prefix="/editor", tags=["editor"])

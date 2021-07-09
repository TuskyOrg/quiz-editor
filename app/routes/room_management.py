from fastapi import APIRouter, Depends

from app import deps
from app.models import RoomModel, TokenPayload

router = APIRouter()


@router.post("/")
def create_room(
    obj_in: RoomModel,
    db=Depends(deps.get_db),
    user_token_payload: TokenPayload = Depends(deps.verify_user_token)
):
    pass

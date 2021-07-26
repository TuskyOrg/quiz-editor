from typing import MutableMapping

import tusky_snowflake
from fastapi import APIRouter, Depends


from app import crud, deps
from app.exceptions import PermissionError403
from app.models import RoomModel, TokenPayload, SubmitedAnswerModel

room_router = APIRouter()


@room_router.post("/management/create")
async def create_room(
    obj_in: RoomModel,
    db=Depends(deps.get_db),
    user_token_payload: TokenPayload = Depends(deps.verify_user_token),
):
    user_snowflake = user_token_payload.sub
    if obj_in.owner_id != user_snowflake:
        raise PermissionError403
    return await crud.room.create(db, obj_in=obj_in)


@room_router.post("/management/close")
async def close_room(
    room_id: tusky_snowflake.Snowflake,
    db=Depends(deps.get_db),
    user_token_payload: TokenPayload = Depends(deps.verify_user_token),
):
    user_snowflake = user_token_payload.sub
    room_obj = await crud.room.get(db, id_=room_id)
    if room_obj["owner_id"] != user_snowflake:
        raise PermissionError403
    return await crud.room.patch(
        db,
        id_=room_id,
        json_patch_request=[{"op": "replace", "path": "/is_active", "value": False}],
    )


@room_router.get("/student/get-room")
async def join_room(
    room_code,
    db=Depends(deps.get_db),
    user_token_payload: TokenPayload = Depends(deps.verify_user_token),
):
    room = await crud.room.get_by_code(db, code=room_code)
    quiz = await crud.quiz.get(db, id=room["quiz_id"])

    # Todo: this is terrible code and needs refactored
    def get_rid_of_answers(m: MutableMapping):
        for k, v in m.items():
            if k == "points":
                m.pop(k)
                continue
            if isinstance(v, MutableMapping):
                get_rid_of_answers(v)
        return m

    student_quiz = get_rid_of_answers(quiz)
    room["quiz"] = student_quiz
    return room


@room_router.post("/student/submit_answers")
async def submit_answers(
    obj_in: SubmitedAnswerModel,
    db=Depends(deps.get_db),
    user_token_payload: TokenPayload = Depends(deps.verify_user_token),
):
    user_snowflake = user_token_payload.sub
    if obj_in.student_id != user_snowflake:
        raise PermissionError403
    # Todo: again, a terrible way to do this.
    #  The architecture was solid before work started on rooms
    return await crud.room.patch(
        db, id_=obj_in.room_id, json_patch_request=["add", "/submitted_answers/-"]
    )

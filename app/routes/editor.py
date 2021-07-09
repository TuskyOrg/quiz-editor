from typing import Dict, List, Any

from fastapi import APIRouter, Body, Depends, Request, status
from fastapi.responses import JSONResponse

from app import crud, deps
from app.models import QuizModel, TokenPayload
from app.exceptions import PermissionError403, NotFoundError404

SNOWFLAKE = int

router = APIRouter()


@router.post("/quiz")
async def create_quiz(
    obj_in: QuizModel,
    db=Depends(deps.get_db),
    user_token_payload: TokenPayload = Depends(deps.verify_user_token),
):
    user_snowflake = user_token_payload.sub
    if obj_in.owner != user_snowflake:
        raise PermissionError403
    quiz = await crud.quiz.create(db, obj_in=obj_in)
    if quiz is None:
        raise NotFoundError404
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=quiz)


@router.get("/quiz", response_model=QuizModel)
async def get_quiz(
    id: SNOWFLAKE,
    db=Depends(deps.get_db),
    user_token_payload: TokenPayload = Depends(deps.verify_user_token),
):
    print("ENTERING THE GET ROUTE")
    user_snowflake = user_token_payload.sub
    quiz = await crud.quiz.get(db, id_=id)
    if quiz is None:
        raise NotFoundError404
    if user_snowflake != quiz["owner"]:
        raise PermissionError403
    return QuizModel(**quiz)


@router.patch("/quiz/{id}")
async def patch_quiz(
    id: SNOWFLAKE,
    json_patch_request: Any = Body(...),
    db=Depends(deps.get_db),
    user_token_payload: TokenPayload = Depends(deps.verify_user_token),
):
    # I have had a lot of trouble trying to type these patch requests that I decided to do it manually
    if not isinstance(json_patch_request, list):
        raise ValueError("A jsonpatch request must be a list")
    print("JSON_PATCH_REQUEST:\t", json_patch_request)
    user_snowflake = user_token_payload.sub
    quiz = await crud.quiz.get(db, id_=id)
    if quiz is None:
        raise NotFoundError404
    if user_snowflake != quiz["owner"]:
        raise PermissionError403
    return await crud.quiz.patch(db, id_=id, json_patch_request=json_patch_request)


@router.delete("/quiz")
async def delete_quiz(
    id: SNOWFLAKE,
    db=Depends(deps.get_db),
    user_token_payload: TokenPayload = Depends(deps.verify_user_token),
):
    user_snowflake = user_token_payload.sub
    quiz = await crud.quiz.get(db, id_=id)
    if quiz is None:
        raise NotFoundError404
    if quiz["owner"] != user_snowflake:
        raise PermissionError403
    await crud.quiz.delete(db, id_=id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

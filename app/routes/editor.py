from typing import Any, List

from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse

from app import crud, deps
from app.models import QuizModel, QuizPrivateSchema, TokenPayload, QuizTitle
from app.exceptions import PermissionError403, NotFoundError404

SNOWFLAKE = int

editor_router = APIRouter()


@editor_router.post("/quiz", response_model=QuizPrivateSchema)
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


@editor_router.get("/quiz", response_model=QuizPrivateSchema)
async def get_quiz(
    id: SNOWFLAKE,
    db=Depends(deps.get_db),
    user_token_payload: TokenPayload = Depends(deps.verify_user_token),
):
    user_snowflake = user_token_payload.sub
    quiz = await crud.quiz.get(db, id_=id)
    if quiz is None:
        raise NotFoundError404
    if user_snowflake != quiz["owner"]:
        raise PermissionError403
    return quiz
    # return QuizPrivateSchema(**quiz)


@editor_router.patch("/quiz/{id}", response_model=QuizPrivateSchema)
async def patch_quiz(
    id: SNOWFLAKE,
    json_patch_request: Any = Body(...),
    db=Depends(deps.get_db),
    user_token_payload: TokenPayload = Depends(deps.verify_user_token),
):
    print("JSON_PATCH_REQUEST:\t", json_patch_request)
    user_snowflake = user_token_payload.sub
    quiz = await crud.quiz.get(db, id_=id)
    if quiz is None:
        raise NotFoundError404
    if user_snowflake != quiz["owner"]:
        raise PermissionError403
    original_quiz = await crud.quiz.get(db, id_=id)
    return await crud.quiz.patch(
        db, original=original_quiz, json_patch_request=json_patch_request
    )


@editor_router.delete("/quiz")
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


@editor_router.get("/quiz-titles", response_model=List[QuizTitle])
async def get_quiz_titles(
    db=Depends(deps.get_db),
    user_token_payload: TokenPayload = Depends(deps.verify_user_token),
):
    user_snowflake = user_token_payload.sub
    x = await crud.quiz.get_titles_by_user(db, user_id=user_snowflake)
    print("Returned objects:\t", x)
    return x

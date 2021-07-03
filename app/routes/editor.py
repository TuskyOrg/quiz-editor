import tusky_users

from fastapi import APIRouter, Depends, HTTPException
from tusky_snowflake import Snowflake
from sqlalchemy.orm import Session

from app import deps, schemas, crud
from app.exceptions import PermissionError403

router = APIRouter()


@router.post("/quiz", response_model=schemas.QuizResponse)
async def create_quiz(
    *,
    db: Session = Depends(deps.get_db),
    user_token_payload: schemas.TokenPayload = Depends(deps.verify_user_token),
    obj_in: schemas.QuizCreate,
):
    user_snowflake = user_token_payload.sub
    if obj_in.owner is not None and obj_in.owner != user_snowflake:
        raise PermissionError403
    quiz = await crud.quiz.create(db, obj_in=obj_in)
    return quiz


@router.get("/quiz", response_model=schemas.QuizResponse)
async def get_quiz(
    *,
    db: Session = Depends(deps.get_db),
    user_token_payload: schemas.TokenPayload = Depends(deps.verify_user_token),
    id: Snowflake
):
    user_snowflake = user_token_payload.sub
    quiz = crud.quiz.get(db, id=id)
    if quiz.owner != user_snowflake:
        raise PermissionError403
    return quiz


@router.patch("/quiz/{quiz_id}", response_model=schemas.QuizResponse)
async def patch_quiz(
    *,
    db: Session = Depends(deps.get_db),
    user_token_payload: schemas.TokenPayload = Depends(deps.verify_user_token),
    quiz_id: Snowflake,
    patch: schemas.QuizPatch,
):
    """
    Use [RFC 6902](https://datatracker.ietf.org/doc/html/rfc6902/) JSON Patch operations to modify the quizzes properties.

    ## Quiz schema (in pseudo-code)
    <!-- Actual JSON Schema (http://json-schema.org/draft-04/schema#) is difficult for humans to parse-->

    ### Quiz (root):

        {
          "id": Snowflake,
          "title": str,
          "owner": Snowflake,
          "questions": List[Question]
        }

    ### Question:

        {
          "id": Snowflake,
          "query": str,
          "type": QuestionType,
          "answers": List[Answer]
        }

    ### Answer:

        {
          "id": Snowflake,
          "text": str,
          "points": number
        }
    """
    quiz = crud.quiz.get(db, id=quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    quiz = crud.quiz.patch(db, db_obj=quiz, patch=patch)
    return quiz

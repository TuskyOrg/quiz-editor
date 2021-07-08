from collections import MutableMapping
from typing import TypeVar, Generic, Type, Optional

import jsonpatch
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import text
from tusky_snowflake import Snowflake, get_snowflake, synchronous_get_snowflake

from app import schemas, models
from app.models import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
PatchSchemaType = TypeVar("PatchSchemaType", bound=BaseModel)


class _CRUDBase(Generic[ModelType, CreateSchemaType, PatchSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        snowflake = await get_snowflake()
        db_obj.id = snowflake
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, id: Snowflake) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).one_or_none()

    def patch(
        self, db: Session, *, db_obj: ModelType, patch: PatchSchemaType
    ) -> ModelType:
        raise NotImplementedError

    def delete(self, db: Session, *, id: Snowflake) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj


def replace_placeholders_with_snowflakes(m: MutableMapping):
    for k, v in m.items():
        if isinstance(k, MutableMapping):
            replace_placeholders_with_snowflakes(m)
        if isinstance(v, list):
            for item in v:
                replace_placeholders_with_snowflakes(item)
        if k == "id":
            # Todo: worry about async (and not fetching useless snowflakes)
            snowflake = synchronous_get_snowflake()
            m["id"] = snowflake


class CRUDQuiz(_CRUDBase[models.Quizzes, schemas.QuizCreate, schemas.QuizPatch]):
    async def patch(
        self, db: Session, *, id: Snowflake, patch: PatchSchemaType
    ) -> Optional[schemas.ORMModel]:
        # Todo: optimize SQL
        c: CursorResult = db.execute(
            text("SELECT id, owner, title FROM quizzes WHERE id = :_id"), {"_id": id}
        )
        quiz: models.Quizzes = c.one_or_none()
        if quiz is None:
            return None

        question_cursor = db.execute(
            "SELECT (id, quiz_id, query, answers) from questions WHERE questions.quiz_id = :_id",
            {"_id": id},
        )
        questions = [dict(q) for q in question_cursor]

        quiz_patches = []
        question_patches = []
        for operation in patch.__root__:
            operation: dict
            if operation["path"] == "/quiz":
                quiz_patches.append(operation)
                continue

            # Todo: use `operation["path"].removeprefix("/quiz")` when upgrading to Python 3.9
            question_patches.append(patch)
            operation["path"] = operation["path"][5:]
            if operation["op"] not in ["add", "replace"]:
                continue
            if not isinstance(operation["value"], MutableMapping):
                continue
            replace_placeholders_with_snowflakes(operation["value"])

        print("QUIZ PATCHES: ", quiz_patches)
        print("QUESTION PATCHES", question_patches)
        q = {**quiz}
        for operation in quiz_patches:
            op = operation["op"]
            if op == "add":
                pass
            if op == "remove":
                pass
            if op == "replace":
                pass
            if op == "move":
                pass
            if op == "copy":
                pass
            if op == "test":
                pass





        s = schemas.QuizInDB(**d)

        c = db.execute(
            text(
                "UPDATE quizzes SET (title, owner) = (:title, :owner) WHERE id = :id RETURNING *"
            ),
            s.dict(),
        )
        quiz = c.one()

        c = db.execute(
            """
            UPDATE answers SET () 
            """
        )


        db.commit()
        return c.one_or_none()


quiz = CRUDQuiz(models.Quizzes)

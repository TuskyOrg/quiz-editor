from typing import TypeVar, Generic, Type, Optional

import jsonpatch
from tusky_snowflake import Snowflake, get_snowflake
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.sql.expression import update
from sqlalchemy.orm import Session

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


class CRUDQuiz(_CRUDBase[models.Quizzes, schemas.QuizCreate, schemas.QuizPatch]):
    def patch(
        self, db: Session, *, id: Snowflake, patch: PatchSchemaType
    ) -> ModelType:
        db_obj: models.Quizzes = db.query(self.model).filter(self.model.id == id).one_or_none()
        ops = [op.dict() for op in patch.__root__]
        patches = jsonpatch.apply_patch(dict(db_obj), ops, in_place=False)
        db.execute(
            update(models.Quizzes).where(models.Quizzes.id == db_obj.id), params=patches
        )
        db.flush(db_obj)
        db.refresh(db_obj)
        return db_obj


quiz = CRUDQuiz(models.Quizzes)

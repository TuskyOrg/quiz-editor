from typing import TypeVar, Generic, Type, Optional

import jsonpatch
from tusky_snowflake import Snowflake, get_snowflake
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
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
        self, db: Session, *, db_obj: ModelType, obj_in: PatchSchemaType
    ) -> ModelType:
        raise NotImplementedError

    def delete(self, db: Session, *, id: Snowflake) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj


class CRUDQuiz(_CRUDBase[models.Quizzes, schemas.QuizCreate, schemas.QuizPatch]):
    def patch(
        self, db: Session, *, db_obj: ModelType, patch: PatchSchemaType
    ) -> ModelType:
        jsonpatch.apply_patch(db_obj, patch, in_place=True)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


quiz = CRUDQuiz(models.Quizzes)

from typing import (
    TypeVar,
    Generic,
    Type,
    Optional,
    Dict,
    List,
    Any,
    Union,
    MutableMapping,
    MutableSequence,
)

import jsonpatch
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from pymongo import ReturnDocument

from app.models import QuizModel

SNOWFLAKE = int

ModelType = TypeVar("ModelType", bound=BaseModel)
PatchType = TypeVar("PatchType", bound=BaseModel)


class _CRUDBase(Generic[ModelType]):
    def __init__(self, collection: str, model: Type[ModelType]):
        self.collection = collection
        self.model = model

    async def create(self, db: AsyncIOMotorClient, *, obj_in: ModelType) -> Dict:
        obj_in_data = jsonable_encoder(obj_in)
        new_obj = await db[self.collection].insert_one(obj_in_data)
        return await db[self.collection].find_one({"_id": new_obj.inserted_id})

    async def get(self, db: AsyncIOMotorClient, *, id_: SNOWFLAKE) -> Optional[Dict]:
        return await db[self.collection].find_one({"_id": id_})

    async def patch(self, db: AsyncIOMotorClient, *, id_: SNOWFLAKE, patch_in):
        raise NotImplementedError

    async def delete(self, db: AsyncIOMotorClient, *, id_: SNOWFLAKE) -> bool:
        delete_result = await db[self.collection].delete_one({"_id": id_})
        if delete_result.deleted_count == 1:
            return True
        return False  # Not found


def _replace_ids_with_oids(x: Union[MutableSequence, MutableMapping]):
    if isinstance(x, MutableMapping):
        for k, v in x.items():
            if isinstance(v, MutableSequence) or isinstance(v, MutableMapping):
                _replace_ids_with_oids(v)
    elif isinstance(x, MutableSequence):
        for v in x:
            if isinstance(v, MutableSequence) or isinstance(v, MutableMapping):
                _replace_ids_with_oids(v)


class CRUDQuiz(_CRUDBase[QuizModel]):
    async def patch(self, db, *, id_: SNOWFLAKE, json_patch_request):
        # Todo: this whole process smells
        orig_quiz = await db[self.collection].find_one({"_id": id_})
        print("ORIG_QUIZ:\t", orig_quiz)
        # Some fields are not allowed to be changed; make sure that they aren't accessed
        patches = jsonpatch.JsonPatch(json_patch_request)
        for p in patches:
            print("PATCHES:\t", patches)
            print("PATCH:\t", p)
            pointer = jsonpatch.JsonPointer(p["path"])

            if pointer.path == "/":
                # We do not allow empty strings as keys
                raise ValueError
            if "owner" in pointer.path:
                raise ValueError
            if "_id" in pointer.path:
                raise ValueError
            if "id" in pointer.path:
                raise ValueError

        print("PREPATCHED QUIZ:\t", orig_quiz)
        patched_quiz = patches.apply(orig_quiz, in_place=False)
        # Replace any "ids" with "_ids" (Snowflakes)
        print("PATCHED QUIZ:\t", patched_quiz)
        quiz_model = QuizModel(**patched_quiz)
        new_quiz = quiz_model.dict(by_alias=True)
        print("NEW QUIZ:\t", new_quiz)

        # We have to make sure that no one has edited the original while we were processing stuff here,
        # so we filter against the entire original, not just the _id
        return await db[self.collection].find_one_and_replace(
            orig_quiz, new_quiz, return_document=ReturnDocument.AFTER
        )


quiz = CRUDQuiz("quizzes", QuizModel)

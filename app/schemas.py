from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel
from tusky_snowflake import Snowflake

# from .pydantic_json_patch import JsonPatchRequest
# from .pydantic_json_patch._pointer import JsonPointer
from .pydantic_json_patch import JsonPatchRequest, JsonPointer


class ORMModel(BaseModel):
    """Mixin for schemas representing an object in a database"""

    class Config:
        orm_mode = True


# Design decision: Instead of each group of classes (for example, QuizCreate, QuizPatch,
# and QuizResponse) sharing a _QuizBase class, shared attributes are repeated.
# Repetition is a small price to pay for clearer code.


#######################################################################################
class AnswerCreate(BaseModel):
    id: str
    text: str
    points: Decimal = Decimal(0)


class AnswerResponse(BaseModel):
    id: Snowflake
    text: str
    points: Decimal = Decimal(0)


class AnswerInDB(ORMModel):
    id: Snowflake
    text: str
    points: Decimal = Decimal(0)


############################################
class QuestionCreate(BaseModel):
    id: str
    query: str
    answers: Optional[List[AnswerCreate]]


class QuestionResponse(BaseModel):
    id: Snowflake
    query: str
    answers: Optional[List[AnswerResponse]]


class QuestionInDB(ORMModel):
    id: Snowflake
    query: str
    answers: Optional[List[AnswerInDB]]


############################################
class QuizCreate(BaseModel):
    owner: Snowflake
    title: str


class QuizPatch(JsonPatchRequest):
    pass


class QuizResponse(ORMModel):
    id: Snowflake  # Immutable
    title: str
    owner: Snowflake
    questions: List[QuestionResponse]


class QuizInDB(ORMModel):
    id: Snowflake  # Immutable
    title: str
    owner: Snowflake
    questions: List[QuestionResponse] = []


#######################################################################################
class TokenPayload(BaseModel):
    # subject
    sub: Optional[Snowflake] = None
    # aud: Optional[List[str]]

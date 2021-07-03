import enum
from decimal import Decimal
from typing import NamedTuple, Type, Tuple, Union, Optional, Any, Dict, List

from tusky_snowflake import Snowflake
from pydantic import BaseModel, Field
from .pydantic_json_patch import JsonPatchRequest

from app.pydantic_json_patch.op import Op, Add, Remove, JsonOp


# Design decision: Instead of each group of classes (for example, QuizCreate, QuizPatch,
# and QuizResponse) sharing a _QuizBase class, shared attributes are repeated.
# Repetition is a small price to pay for clearer code.


#######################################################################################
class AnswerResponse(BaseModel):
    id: Snowflake
    text: str
    points: Decimal = Decimal(0)


class QuestionType(enum.Enum):
    # SHORT_ANSWER = ...
    # ESSAY = ...
    MULTIPLE_CHOICE = "multiple choice"


class QuestionResponse(BaseModel):
    id: Snowflake
    query: str
    type: QuestionType
    answers: Optional[List[AnswerResponse]]


class QuizCreate(BaseModel):
    owner: Snowflake
    title: str


class QuizPatch(JsonPatchRequest):
    # Schema:
    #
    #   title: str
    #   owner: Snowflake
    #   questions: List[Question]
    #
    #   class Question(BaseModel):
    #
    pass


class QuizResponse(BaseModel):
    id: Snowflake  # Immutable
    title: str
    owner: Snowflake
    questions: List[QuestionResponse]

    class Config:
        orm_mode = True


#######################################################################################
class TokenPayload(BaseModel):
    # subject
    sub: Optional[Snowflake] = None
    # aud: Optional[List[str]]

""" Module for models & schemas.

A model is a representation of a database object.

A schema is a object returned by the API
"""
import random
import string
from typing import Optional, List, Union

from pydantic import BaseModel, Field

import tusky_snowflake


class _Model(BaseModel):
    # Todo: make async
    id: tusky_snowflake.Snowflake = Field(
        default_factory=tusky_snowflake.synchronous_get_snowflake,
        alias="_id",
    )

    class Config:
        allow_population_by_field_name = True


class _Schema(BaseModel):
    id: tusky_snowflake.Snowflake = Field(..., alias="_id")

    class Config:
        allow_population_by_field_name = True


#######################################################################################

class AnswerModel(_Model):
    text: str
    points: float = Field(0)


class QuestionModel(_Model):
    query: str
    answers: List[AnswerModel] = []


class QuizModel(_Model):
    title: str
    owner: tusky_snowflake.Snowflake
    questions: List[QuestionModel] = []


################################################################

class AnswerPrivateSchema(_Schema):
    text: str
    points: float = Field(0)


class QuestionPrivateSchema(_Schema):
    query: str
    answers: List[AnswerPrivateSchema] = []


class QuizPrivateSchema(_Schema):
    title: str
    owner: tusky_snowflake.Snowflake
    questions: List[QuestionPrivateSchema] = []


################################################################

class QuizTitle(_Schema):
    title: str


################################################################

class AnswerPublicSchema(_Schema):
    text: str


class QuestionPublicSchema(_Schema):
    query: str
    answers: List[AnswerPublicSchema] = []


class QuizPublicSchema(_Schema):
    title: str
    owner: tusky_snowflake.Snowflake
    questions: List[QuestionPublicSchema] = []


################################################################

class SubmitedAnswerModel(_Model):
    student_id: tusky_snowflake.Snowflake
    room_id: tusky_snowflake.Snowflake
    question_id: tusky_snowflake.Snowflake
    answer: Union[tusky_snowflake.Snowflake, str]


#######################################################################################

def _generate_code() -> str:
    return "".join([random.choice(string.ascii_uppercase) for _ in range(5)])


class RoomModel(_Model):
    # A unique partial index ensures that two active room cannot share the same code
    # (Logic in mongo-init.js). Unfortunately, it doesn't work yet.
    owner_id: tusky_snowflake.Snowflake
    quiz_id: tusky_snowflake.Snowflake
    code: str = Field(default_factory=_generate_code)
    is_active: bool = True
    submitted_answers: List[SubmitedAnswerModel] = []


class RoomPublicSchema(_Schema):
    owner_id: tusky_snowflake.Snowflake
    quiz_id: tusky_snowflake.Snowflake
    code: str
    is_active: bool


#######################################################################################
class TokenPayload(BaseModel):
    sub: Optional[tusky_snowflake.Snowflake] = None  # subject
    # aud: Optional[List[str]]

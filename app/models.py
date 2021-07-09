# MongoDB cares little for the differences between models and schemas 😛
from decimal import Decimal
from numbers import Number
from typing import Optional, List

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


# class _Response(BaseModel):
#     _id: int = Field(..., alias="id")
#
#
# class AnswerResponse(_Response):
#     text: str
#     points: Optional[Decimal]
#
#
# class QuestionResponse(_Response):
#     query: str
#     answers: List[AnswerResponse] = []
#
#
# class QuizResponse(_Response):
#     title: str
#     owner: tusky_snowflake.Snowflake
#     questions: List[QuestionResponse] = []


#######################################################################################
class TokenPayload(BaseModel):
    sub: Optional[tusky_snowflake.Snowflake] = None  # subject
    # aud: Optional[List[str]]

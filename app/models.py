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


class SubmitedAnswerModel(_Model):
    student_id: tusky_snowflake.Snowflake
    room_id: tusky_snowflake.Snowflake
    question_id: tusky_snowflake.Snowflake
    answer: Union[tusky_snowflake.Snowflake, str]


class RoomModel(_Model):
    # A unique partial index ensures that two active room cannot share the same code
    # (Logic in mongo-init.js). Unfortunately, it doesn't work yet.
    owner_id: tusky_snowflake.Snowflake
    quiz_id: tusky_snowflake.Snowflake
    code: str
    is_active: bool
    submitted_answers: List[SubmitedAnswerModel]


#######################################################################################
class TokenPayload(BaseModel):
    sub: Optional[tusky_snowflake.Snowflake] = None  # subject
    # aud: Optional[List[str]]

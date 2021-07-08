# Notice on modifying models:
#   Many models are accessed using raw sql.
#   Remember to also modify their CRUD operation after adding or deleting fields.

from sqlalchemy import Column, BIGINT, TEXT, ForeignKey
from sqlalchemy.orm import (
    DeclarativeMeta,
    declared_attr,
    relationship,
    as_declarative,
)
from sqlalchemy_json import NestedMutableJson as NESTED_MUTABLE_JSON

SNOWFLAKE = BIGINT


@as_declarative()
class Base:
    __metaclass__: DeclarativeMeta
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically"""
        n = cls.__name__
        # ExampleTable -> example_table
        return n[0].lower() + "".join(
            "_" + x.lower() if x.isupper() else x for x in n[1:]
        )


class Quizzes(Base):
    id = Column(SNOWFLAKE, primary_key=True, index=True)
    owner = Column(SNOWFLAKE)
    title = Column(TEXT)
    questions = relationship("Questions")


class Questions(Base):
    id = Column(SNOWFLAKE, primary_key=True, index=True)
    quiz_id = Column(SNOWFLAKE, ForeignKey("quizzes.id"))
    query = Column(TEXT)
    answers = Column(NESTED_MUTABLE_JSON, nullable=True)

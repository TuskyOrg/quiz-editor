from collections.abc import MutableMapping

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

    def _keys(self):
        return ["id", "owner", "title", "questions"]

    def __getitem__(self, item):
        # Todo: this code smells terrible; there has to be a better way to do this
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __delitem__(self, key):
        raise NotImplementedError

    def __iter__(self):
        for k in self._keys():
            yield k

    def __len__(self):
        return len(self._keys())

    def keys(self):
        return ["id", "owner", "title", "questions"]


MutableMapping.register(Quizzes)


class Questions(Base):
    id = Column(SNOWFLAKE, primary_key=True, index=True)
    quiz_id = Column(SNOWFLAKE, ForeignKey("quizzes.id"))
    query = Column(TEXT)
    answers = Column(NESTED_MUTABLE_JSON, nullable=True)

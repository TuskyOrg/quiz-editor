__all__ = (
    # Patch Request: likely the only thing you'll have to import
    "JsonPatchRequest",
    # Operations
    "Add",
    "Remove",
    "Replace",
    "Move",
    "Copy",
    "Test",
    # Base operation
    "JsonOp",
)
from typing import Literal, Any, Tuple, Type, TypeVar, Union

from pydantic import BaseModel, Field, validator

# JSON Patch RFC: https://datatracker.ietf.org/doc/html/rfc6902
from app.pydantic_json_patch._pointer import JsonPointer
from app.pydantic_json_patch.exceptions import MalformedPatchDocument


class JsonOp(BaseModel):
    pass


class Add(JsonOp):
    op: Literal["add"]
    path: JsonPointer
    value: Any


class Remove(JsonOp):
    op: Literal["remove"]
    path: JsonPointer


class Replace(JsonOp):
    op: Literal["replace"]
    path: JsonPointer
    value: Any


class Move(JsonOp):
    op: Literal["move"]
    from_: JsonPointer = Field(..., alias="from")
    path: JsonPointer


class Copy(JsonOp):
    op: Literal["copy"]
    from_: JsonPointer = Field(..., alias="from")
    path: JsonPointer


class Test(JsonOp):
    op: Literal["test"]
    path: JsonPointer
    value: Any


Op = Union[Add, Union[Remove, Union[Replace, Union[Move, Union[Copy, Test]]]]]


class JsonPatchRequest(BaseModel):
    __root__: Tuple[Op, ...]

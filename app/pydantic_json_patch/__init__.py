# __all__ = ("JsonPatchRequest", "JsonPointer", "op", "exceptions")
# from . import exceptions
# from . import op
# from ._pointer import JsonPointer
# from .op import JsonPatchRequest
from typing import List, Dict

import jsonpatch
import jsonpointer
from pydantic import BaseModel, Field, validator


class JsonPatchRequest(BaseModel):
    __root__: List[Dict] = Field(...)

    @validator("__root__")
    def to_json_patch(cls, v):
        return jsonpatch.JsonPatch(v)



JsonPointer = jsonpointer.JsonPointer
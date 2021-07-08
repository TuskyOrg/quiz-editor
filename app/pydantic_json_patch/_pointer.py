# from pydantic import BaseModel, Field
#
#
# class JsonPointer(BaseModel):
#     __root__: str = Field(..., regex="(/(([^/~])|(~[01]))*)")
#     # @validator("__root__")
#     # def validate_pointer(cls, v):
#     #     jsonpointer.JsonPointer(v)
#     #     return v
#     #

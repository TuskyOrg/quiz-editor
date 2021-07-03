__all__ = (
    "MalformedPatchDocument",
    "UnsupportedPatchDocument",
    "UnprocessableRequest",
    "ResourceNotFound",
    "ConflictingState",
    "ConflictingModification",
    "ConcurrentModification",
    # Base exception
    "JsonPatchException",
)

from http import HTTPStatus


class JsonPatchException:
    # https://datatracker.ietf.org/doc/html/rfc5789#section-2.2
    pass


class MalformedPatchDocument(JsonPatchException):
    status_code = HTTPStatus.BAD_REQUEST  # 400


class UnsupportedPatchDocument(JsonPatchException):
    status_code = HTTPStatus.UNSUPPORTED_MEDIA_TYPE  # 415


class UnprocessableRequest(JsonPatchException):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY  # 422


class ResourceNotFound(JsonPatchException):
    status_code = HTTPStatus.NOT_FOUND  # 404


class ConflictingState(JsonPatchException):
    status_code = HTTPStatus.CONFLICT  # 409


class ConflictingModification(JsonPatchException):
    status_code = HTTPStatus.CONFLICT  # 409
    # When a client uses either the If-Match or If-Unmodified-Since header to define
    # a precondition, and that precondition failed, then the 412 (Precondition
    # Failed) error is most helpful to the client.
    # status_code = HTTPStatus.PRECONDITION_FAILED  # 412


class ConcurrentModification(JsonPatchException):
    status_code = HTTPStatus.CONFLICT  # 409

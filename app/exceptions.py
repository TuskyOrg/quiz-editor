from fastapi import status
from fastapi.exceptions import HTTPException as _HTTPException


class TuskyHTTPException(_HTTPException):
    __suppress_context__ = False


class InvalidCredentials400(TuskyHTTPException):
    def __init__(self):
        super(InvalidCredentials400, self).__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate credentials",
        )


class PermissionError403(TuskyHTTPException):
    def __init__(self):
        super(PermissionError403, self).__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform the action",
        )


class NotFoundError404(TuskyHTTPException):
    def __init__(self):
        super(NotFoundError404, self).__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
        )

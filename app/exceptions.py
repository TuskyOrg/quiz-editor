from fastapi import status
from fastapi.exceptions import HTTPException


class InvalidCredentials400(HTTPException):
    def __init__(self):
        super(InvalidCredentials400, self).__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate credentials",
        )


class PermissionError403(HTTPException):
    def __init__(self):
        super(PermissionError403, self).__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform the action",
        )

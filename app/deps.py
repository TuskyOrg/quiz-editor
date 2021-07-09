import jwt
from fastapi import Depends
from fastapi.security import HTTPBearer
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import ValidationError

from app import database, models
from app.core import settings
from app.exceptions import InvalidCredentials400

_reusable_bearer = HTTPBearer(bearerFormat="jwt")


async def verify_user_token(
    token: HTTPBearer = Depends(_reusable_bearer),
) -> models.TokenPayload:
    try:

        payload = jwt.decode(
            token.credentials,
            settings.TUSKY_IDENTITY_SERVICE_SHARED_SECRET,
            algorithms=settings.TUSKY_IDENTITY_SERVICE_ALGORITHMS,
            audience=[settings.TUSKY_IDENTITY_SERVICE_TOKEN_AUDIENCE],
        )
        token_data = models.TokenPayload(**payload)
    except (jwt.PyJWTError, ValidationError) as err:
        raise InvalidCredentials400 from err
    # At the time of writing,
    # token_data is just the "sub" field containing the user's snowflake.
    # It would make sense to return the snowflake directly,
    # but returning "token_data" lets us add more fields in the future more easily.
    return token_data


async def get_db() -> AsyncIOMotorClient:
    return database.db.client

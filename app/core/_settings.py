from typing import Optional, Dict, Any, List, Union

from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    DEBUG_MODE: bool = True

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    TUSKY_IDENTITY_SERVICE_SHARED_SECRET: str
    TUSKY_IDENTITY_SERVICE_ALGORITHMS: List[str]
    TUSKY_IDENTITY_SERVICE_TOKEN_AUDIENCE: Union[List[str], str]

    class Config:
        case_sensitive = True


settings = Settings()

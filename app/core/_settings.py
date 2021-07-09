from typing import Optional, Dict, Any, List

from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    IS_PRODUCTION: bool = False

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

    MONGO_HOST: str
    MONGO_PORT: int
    # MONGO_USER: str
    # MONGO_PASS: str
    MONGO_DB: str
    MONGO_URL: Optional[str] = None

    @validator("MONGO_URL")
    def assemble_mongo_connection(cls, v, values):
        if isinstance(v, str):
            return v
        # return f"mongodb://{values.get('MONGO_USER')}:{values.get('MONGO_PASS')}@{values.get('MONGO_HOST')}:{values.get('MONGO_PORT')}/{values.get('MONGO_DB')}"
        return f"mongodb://{values.get('MONGO_HOST')}:{values.get('MONGO_PORT')}/{values.get('MONGO_DB')}"

    TUSKY_IDENTITY_SERVICE_SHARED_SECRET: str
    TUSKY_IDENTITY_SERVICE_ALGORITHMS: List[str]
    TUSKY_IDENTITY_SERVICE_TOKEN_AUDIENCE: str

    class Config:
        case_sensitive = True


settings = Settings()

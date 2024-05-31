import secrets
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    title: str
    version: str
    host: str
    port: int
    scheme: str

    secret_key: Optional[str] = Field(default_factory=lambda: secrets.token_urlsafe(64))
    algorithm: Optional[str] = Field(default="HS256")
    access_token_expire_minutes: Optional[int] = Field(default=30)
    refresh_token_expire_hours: Optional[int] = Field(default=24)

    redis_host: str
    redis_port: int
    redis_password: Optional[str] = Field(default="")

    database_hostname: str
    database_port: int
    database_password: str
    database_name: str
    database_username: str

    class Config:
        env_file = ".env"


settings = Settings()

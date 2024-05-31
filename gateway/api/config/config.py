import secrets
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    title: str
    version: str

    mongo_username: str
    mongo_password: str
    mongo_host: str
    mongo_port: int

    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_username: str
    rabbitmq_password: str

    auth_uri: str

    redis_host: str
    redis_port: int
    redis_password: Optional[str] = Field(default="")

    class Config:
        env_file = ".env"


settings = Settings()

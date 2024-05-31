from pydantic import Field, validator
from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_username: str
    rabbitmq_password: str

    email_from: str
    app_password: str

    @validator("app_password",pre=True)
    @classmethod
    def validate_app_password(cls,v):
        return v.replace("-"," ")
    class Config:
        env_file = ".env"

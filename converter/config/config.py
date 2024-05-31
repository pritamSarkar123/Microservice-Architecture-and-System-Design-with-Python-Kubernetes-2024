from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    rabbitmq_host: str 
    rabbitmq_port: int 
    rabbitmq_username: str 
    rabbitmq_password: str 

    mongo_username: str 
    mongo_password: str 
    mongo_host: str 
    mongo_port: int 

    class Config:
        env_file = ".env"


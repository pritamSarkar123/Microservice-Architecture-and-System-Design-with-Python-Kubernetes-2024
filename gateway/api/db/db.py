# from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from ..config import settings

print(settings.auth_uri)


client = MongoClient(
    f"mongodb://{settings.mongo_username}:{settings.mongo_password}@{settings.mongo_host}",
    port=settings.mongo_port,
)

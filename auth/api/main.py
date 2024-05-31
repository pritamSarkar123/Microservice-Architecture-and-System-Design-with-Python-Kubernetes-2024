from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
from .config import settings
from .database import engine
from .models import Base
from .routers import auth_router
from .utils.rate_limit_handler import get_redis_connection

app = FastAPI(
    title=settings.title,
    version=settings.version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
while True:
    try:
        Base.metadata.create_all(bind=engine)
        break
    except Exception as e:
        print(f"Failed to create database. Retrying in 2 seconds. Error: {str(e)}")
        time.sleep(2)

app.include_router(auth_router.router)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from .config import settings
from .routers import auth_router, file_handler

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

app.include_router(auth_router.router)
app.include_router(file_handler.router)

from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    email: str
    password: str


class UserReturn(BaseModel):
    email: str
    admin: Optional[bool]

    class Config:
        from_attributes = True

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class RefreshToken(BaseModel):
    refresh_token: str


class AccessToken(BaseModel):
    access_token: str
    token_type: str



class TokenForValidationForPasswordReset(BaseModel):
    token: str
    new_password: str
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


class TokenForValidation(BaseModel):
    token: str


class TokenForValidationForPasswordReset(TokenForValidation):
    new_password: str


class TokenValidation(BaseModel):
    valid: bool
    admin: bool
    email: str

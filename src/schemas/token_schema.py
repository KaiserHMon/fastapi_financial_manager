from pydantic import BaseModel
import datetime


class TokenData(BaseModel):
    username: str | None = None
    scopes: str | None
    issued_at: datetime


class Token(BaseModel):
    access_token: str
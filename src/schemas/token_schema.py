from pydantic import BaseModel
import datetime


class TokenData(BaseModel):
    username: str | None = None
    scopes: str | None = None
    issued_at: datetime.datetime


class Token(BaseModel):
    access_token: str
    token_type: str
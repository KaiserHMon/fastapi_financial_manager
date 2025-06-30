from pydantic import BaseModel
import datetime


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []
    issued_at: datetime
    expiration: datetime


class Token(BaseModel):
    access_token: str
    token_type: str
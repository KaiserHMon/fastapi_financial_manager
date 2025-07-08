from pydantic import BaseModel
import datetime


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] | None = None
    issued_at: datetime.datetime 
    expired_at: datetime.datetime | None = None
    jti: str | None = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str
    

class LogoutRequest(BaseModel):
    refresh_token: str

class LogoutResponse(BaseModel):
    detail: str
    

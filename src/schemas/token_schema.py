from pydantic import BaseModel
from datetime import datetime


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] | None = None
    issued_at: datetime 
    expired_at: datetime | None = None
    jti: str | None = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str
    

class LogoutRequest(BaseModel):
    refresh_token: str

class LogoutResponse(BaseModel):
    detail: str
    

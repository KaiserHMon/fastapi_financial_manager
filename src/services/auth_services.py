from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from schemas.token_schema import TokenData
from exceptions.http_errors import CREDENTIALS_EXCEPTION
from services.user_services import get_user
from dependencies import get_async_db

from datetime import timedelta
from typing import Annotated
from dotenv import load_dotenv
import os

from jose import JWTError, jwt


load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


oauth_bearer = OAuth2PasswordBearer(tokenUrl='login', scopes={"me": "Get user information"})


def create_access_token(token_data: TokenData):
        access_token = { "sub": token_data.username,
                        "scopes": token_data.scopes,
                        "iat": token_data.issued_at,
                        "exp": token_data.issued_at + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
                        "token_type": "access" }
                        
        return {"access_token": jwt.encode(access_token, SECRET_KEY, JWT_ALGORITHM)}


def create_refresh_token(token_data: TokenData):
        refresh_token = { "sub": token_data.username,
                        "scopes": token_data.scopes,
                        "iat": token_data.issued_at,
                        "exp": token_data.issued_at + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
                        "token_type": "refresh" }
        
        return {"refresh_token": jwt.encode(refresh_token, SECRET_KEY, JWT_ALGORITHM)}



async def auth_token(token: Annotated[str, Depends(oauth_bearer)]):
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise CREDENTIALS_EXCEPTION
            
        return await get_user(username, get_async_db())
        
    except JWTError:
        raise CREDENTIALS_EXCEPTION
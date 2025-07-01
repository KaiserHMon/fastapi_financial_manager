from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
import datetime

from schemas.token_schema import Token, TokenData
from dependencies import get_async_db
from exceptions.http_errors import USER_NOT_FOUND, WRONG_PASSWORD

from services.user_services import get_user
from services.password_services import verify_password
from services.auth_services import create_access_token


auth = APIRouter()

oauth_bearer = OAuth2PasswordRequestForm(tokenUrl='login', scopes={"me": "Get user information"})


@auth.post("/login")
async def login_for_access_token(formdata: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: AsyncSession = Depends(get_async_db))-> Token:
    
    user = await get_user(formdata.username, db)
    if not user:
        raise USER_NOT_FOUND
    
    is_password_correct = verify_password(plain_password=formdata.password,
                                                hashed_password=user.password)
    if not is_password_correct:
        raise WRONG_PASSWORD
    
    access_token = create_access_token(TokenData(username=formdata.username, scopes=formdata.scopes, 
                                                 issued_at=datetime.now()))
    
    return access_token

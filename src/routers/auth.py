from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from schemas.token_schema import Token, TokenData
from services.user_services import get_user, verify_password
from dependencies import get_async_db
from exceptions.http_errors import USER_NOT_FOUND, WRONG_PASSWORD
from services.auth_services import create_access_token

from typing import Annotated
import datetime


auth = APIRouter()

oauth_bearer = OAuth2PasswordRequestForm(tokenUrl='login', scopes={"me": "Get user information"})


@auth.post("/login")
async def login_for_access_token(formdata: Annotated[OAuth2PasswordRequestForm,
                                                     Depends()]) -> Token:
    user = get_user(formdata.username, get_async_db())
    if not user:
        raise USER_NOT_FOUND
    
    password = verify_password(formdata.password, user)
    if not password:
        raise WRONG_PASSWORD
    
    access_token = create_access_token(TokenData(formdata.username, formdata.scopes, 
                                                 datetime.now()))
    
    return access_token

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
import datetime

from schemas.token_schema import Token, TokenData, LogoutRequest
from dependencies import get_async_db
from exceptions.http_errors import USER_NOT_FOUND, WRONG_PASSWORD, CREDENTIALS_EXCEPTION
from models.token_denylist_model import TokenDenylist

from services.user_services import get_user
from services.password_services import verify_password
from services.auth_services import create_access_token, create_refresh_token, auth_refresh_token, auth_access_token, SECRET_KEY, JWT_ALGORITHM

from jose import jwt


auth = APIRouter()


@auth.post("/login", response_model=Token, summary="User login", description="Logs in a user and returns an access and refresh token.")
async def login_for_tokens(formdata: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: AsyncSession = Depends(get_async_db)):
    
    user = await get_user(formdata.username, db)
    if not user:
        raise USER_NOT_FOUND
    
    is_password_correct = verify_password(plain_password=formdata.password,
                                                hashed_password=user.password)
    if not is_password_correct:
        raise WRONG_PASSWORD
    
    token_data = TokenData(username=formdata.username, scopes=" ".join(formdata.scopes), 
                                                 issued_at=datetime.datetime.now())
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return Token(access_token=access_token['access_token'],
                 refresh_token=refresh_token['refresh_token'],
                 token_type='bearer')


@auth.post("/refresh", summary="Refresh access token", description="Refreshes an access token using a valid refresh token.")
async def refresh_access_token(token: dict = Depends(auth_refresh_token)):
    return token


@auth.post("/logout", summary="User logout", description="Logs out a user by adding the refresh token to a denylist.")
async def logout(logout_request: LogoutRequest, 
                 db: AsyncSession = Depends(get_async_db),
                 current_user: dict = Depends(auth_access_token)):
    
    try:
        payload = jwt.decode(
            logout_request.refresh_token, SECRET_KEY, algorithms=[JWT_ALGORITHM]
        )
        jti = payload.get("jti")
        exp = payload.get("exp")

        # Add the jti to the denylist
        denylist_entry = TokenDenylist(jti=jti, exp=exp)
        db.add(denylist_entry)
        await db.commit()

        return {"detail": "Successfully logged out"}

    except jwt.ExpiredSignatureError:
        raise CREDENTIALS_EXCEPTION # Refresh token is expired
    except jwt.InvalidTokenError:
        raise CREDENTIALS_EXCEPTION # Invalid refresh token
    except Exception as e:
        # Log the exception for debugging
        print(f"Error during logout: {e}")
        raise CREDENTIALS_EXCEPTION # Generic error
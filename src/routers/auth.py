from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
import datetime

from ..schemas.token_schema import (
    Token,
    TokenData,
    LogoutRequest,
    LogoutResponse,
    AccessTokenResponse,
)
from ..dependencies import get_async_db
from ..exceptions.http_errors import USER_NOT_FOUND, WRONG_PASSWORD

from ..services import user_services, password_services, auth_services


auth = APIRouter()


@auth.post(
    "/login",
    response_model=Token,
    summary="User login",
    description="Logs in a user and returns an access and refresh token.",
)
async def login_for_tokens(
    formdata: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_async_db),
):
    user = await user_services.get_user(db, formdata.username)
    if not user:
        raise USER_NOT_FOUND

    is_password_correct = password_services.verify_password(
        plain_password=formdata.password, hashed_password=user.password
    )
    if not is_password_correct:
        raise WRONG_PASSWORD

    token_data = TokenData(
        username=formdata.username,
        scopes=formdata.scopes.split() if formdata.scopes else [],
        issued_at=datetime.datetime.now(),
    )

    access_token = auth_services.create_access_token(token_data)
    refresh_token = auth_services.create_refresh_token(token_data)

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@auth.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Refresh access token",
    description="Refreshes an access token using a valid refresh token.",
)
async def refresh_access_token(
    new_token: str = Depends(auth_services.auth_refresh_token),
):
    return {"access_token": new_token, "token_type": "bearer"}


@auth.post(
    "/logout",
    response_model=LogoutResponse,
    summary="User logout",
    description="Logs out a user by adding the refresh token to a denylist.",
)
async def logout(
    logout_request: LogoutRequest,
    db: AsyncSession = Depends(get_async_db),
    token: str = Depends(auth_services.oauth_bearer),
):
    await auth_services.add_token_to_denylist(db, logout_request.refresh_token)
    return {"detail": "Successfully logged out"}
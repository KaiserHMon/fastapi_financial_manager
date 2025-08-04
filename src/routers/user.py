from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from schemas.user_schema import UserIn, UserOut, UserBase
from exceptions.http_errors import (
    USER_CREATION_FAILED,
    USER_ALREADY_EXISTS,
    SERVER_ERROR,
    EMAIL_ALREADY_EXISTS,
)
from dependencies import get_async_db
from services.auth_services import auth_access_token
from models.user_model import UserModel
from services.user_services import UserServices

user = APIRouter()


@user.post("/register", response_model=UserOut, status_code=201)
async def register_user(user_in: UserIn, db: AsyncSession = Depends(get_async_db)):
    user_services = UserServices(db)
    existing_user = await user_services.get_user(user_in.username)
    if existing_user:
        raise USER_ALREADY_EXISTS

    existing_email = await user_services.get_user_by_email(user_in.email)
    if existing_email:
        raise EMAIL_ALREADY_EXISTS

    try:
        created_user = await user_services.create_user(user_in)
        return created_user
    except Exception:
        raise USER_CREATION_FAILED


@user.get("/me", response_model=UserOut)
async def get_current_user(
    current_user: Annotated[UserModel, Depends(auth_access_token)]
):
    return current_user


@user.put("/me", response_model=UserOut)
async def update_current_user_endpoint(
    user_in: UserBase,
    current_user: Annotated[UserModel, Depends(auth_access_token)],
    db: AsyncSession = Depends(get_async_db),
):
    user_services = UserServices(db)
    try:
        updated_user = await user_services.update_user(current_user, user_in)
        return updated_user
    except Exception:
        raise USER_CREATION_FAILED


@user.delete("/me", status_code=204)
async def delete_current_user(
    current_user: Annotated[UserModel, Depends(auth_access_token)],
    db: AsyncSession = Depends(get_async_db),
):
    user_services = UserServices(db)
    try:
        await user_services.delete_user(current_user)
        return {"detail": "User deleted successfully"}
    except Exception:
        raise SERVER_ERROR

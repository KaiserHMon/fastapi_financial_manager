from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from ..schemas.user_schema import UserIn, UserOut, UserBase
from ..exceptions.http_errors import (
    USER_CREATION_FAILED,
    USER_ALREADY_EXISTS,
    SERVER_ERROR,
    EMAIL_ALREADY_EXISTS,
    USER_NOT_FOUND
)
from ..dependencies import get_async_db
from ..services import auth_services, user_services
from ..models.user_model import UserModel

user = APIRouter()


@user.post("/register", response_model=UserOut, status_code=201)
async def register_user(user_in: UserIn, db: AsyncSession = Depends(get_async_db)):
    existing_user = await user_services.get_user(db, user_in.username)
    if existing_user:
        raise USER_ALREADY_EXISTS

    existing_email = await user_services.get_user_by_email(db, user_in.email)
    if existing_email:
        raise EMAIL_ALREADY_EXISTS

    try:
        created_user = await user_services.create_user(db, user_in)
        return created_user
    except Exception:
        raise USER_CREATION_FAILED


@user.get("/me", response_model=UserOut)
async def get_current_user(
    current_user: UserModel = Depends(auth_services.auth_access_token)
):
    return UserOut.model_validate(current_user)


@user.put("/me", response_model=UserOut)
async def update_current_user_endpoint(
    user_in: UserBase,
    current_user: UserModel = Depends(auth_services.auth_access_token),
    db: AsyncSession = Depends(get_async_db),
):
    try:
        updated_user = await user_services.update_user(db, current_user, user_in)
        return updated_user
    except Exception:
        raise USER_CREATION_FAILED


@user.delete("/me", status_code=204)
async def delete_current_user(
    current_user: UserModel = Depends(auth_services.auth_access_token),
    db: AsyncSession = Depends(get_async_db),
):
    try:
        await user_services.delete_user(db, current_user)
        return {"detail": "User deleted successfully"}
    except Exception:
        raise SERVER_ERROR


@user.get("/{user_id}", response_model=UserOut)
async def get_user_by_id(
    user_id: int,
    current_user: UserModel = Depends(auth_services.auth_access_token),
    db: AsyncSession = Depends(get_async_db),
):
    try:
        user = await user_services.get_user_by_id(db, user_id)
        if not user:
            raise USER_NOT_FOUND
        # Convertimos el modelo SQLAlchemy a Pydantic
        return UserOut.model_validate(user)
    except Exception:
        raise SERVER_ERROR

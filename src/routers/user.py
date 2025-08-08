from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated
from datetime import date

from ..schemas.user_schema import UserIn, UserOut, UserBase
from ..schemas.history_schema import HistoryOut
from ..exceptions.http_errors import (
    USER_CREATION_FAILED,
    USER_ALREADY_EXISTS,
    SERVER_ERROR,
    EMAIL_ALREADY_EXISTS,
    USER_NOT_FOUND
)
from ..dependencies import get_async_db
from ..services import auth_services, user_services, history_services
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
async def update_current_user(
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
async def get_user_id(
    user_id: int,
    current_user: UserModel = Depends(auth_services.auth_access_token),
    db: AsyncSession = Depends(get_async_db),
):
    try:
        user = await user_services.get_user_by_id(db, user_id)
        if not user:
            raise USER_NOT_FOUND
        return UserOut.model_validate(user)
    except Exception:
        raise SERVER_ERROR


@user.get("/me/history", response_model=List[HistoryOut])
async def get_user_history(
    current_user: UserModel = Depends(auth_services.auth_access_token),
    db: AsyncSession = Depends(get_async_db),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    try:
        return await history_services.get_history_entries(db, current_user,
                                                          from_date, to_date, skip, limit)
    except Exception:
        raise SERVER_ERROR
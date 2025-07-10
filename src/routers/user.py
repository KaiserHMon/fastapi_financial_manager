from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from schemas.user_schema import UserBase, UserIn, UserOut, UserInDB
from exceptions.http_errors import USER_CREATION_FAILED, USER_ALREADY_EXISTS, USER_NOT_FOUND
from dependencies import get_async_db

from services.user_services import create_user, get_user

user = APIRouter()

@user.post("/register", response_model=UserOut, status_code=201)
async def register_user(user_in: UserIn, db: AsyncSession = Depends(get_async_db)):
    existing_user = await get_user(user_in.username, db)
    if existing_user:
        raise USER_ALREADY_EXISTS
    
    else:
        try:
            created_user = await create_user(user_in, db)
            return created_user
        except Exception:
            raise USER_CREATION_FAILED
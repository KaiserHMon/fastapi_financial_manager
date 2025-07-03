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
        """ try:
            user_db = UserInDB(**user_in.model_dump())
            created_user = await create_user(user_db, db)
            return UserOut(**created_user.dict())
        except Exception as e:
            raise USER_CREATION_FAILED from e """
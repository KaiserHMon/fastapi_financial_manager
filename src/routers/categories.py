from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List

from dependencies import get_async_db
from services import auth_services, categories_services
from exceptions.http_errors import (
    CATEGORY_NOT_FOUND,
    CATEGORY_CREATION_FAILED,
    CATEGORY_ALREADY_EXISTS,
)
from schemas.categories_schema import CategoriesIn, CategoriesOut
from models.user_model import UserModel

categories = APIRouter()


@categories.post(
    "/", response_model=CategoriesOut, status_code=status.HTTP_201_CREATED
)
async def add_category(
    category: CategoriesIn,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_services.auth_access_token),
):
    category_exists = await categories_services.get_category_by_name(
        db, category.name, current_user
    )
    if category_exists:
        raise CATEGORY_ALREADY_EXISTS
    try:
        return await categories_services.create_category(db, category, current_user)
    except IntegrityError:
        raise CATEGORY_CREATION_FAILED


@categories.get("/", response_model=List[CategoriesOut])
async def list_categories(
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_services.auth_access_token),
):
    return await categories_services.get_categories(db, current_user)


@categories.get("/{category_id}", response_model=CategoriesOut)
async def retrieve_category(
    category_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_services.auth_access_token),
):
    category = await categories_services.get_category(db, category_id, current_user)
    if not category:
        raise CATEGORY_NOT_FOUND
    return category


@categories.put("/{category_id}", response_model=CategoriesOut)
async def modify_category(
    category_id: int,
    category_in: CategoriesIn,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_services.auth_access_token),
):
    category_exists = await categories_services.get_category_by_name(
        db, category_in.name, current_user
    )
    if category_exists:
        raise CATEGORY_ALREADY_EXISTS
    try:
        updated_category = await categories_services.update_category(
            db, category_id, category_in, current_user
        )
        if not updated_category:
            raise CATEGORY_NOT_FOUND
        return updated_category
    except IntegrityError:
        raise CATEGORY_CREATION_FAILED


@categories.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_category(
    category_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_services.auth_access_token),
):
    category_to_delete = await categories_services.delete_category(
        db, category_id, current_user
    )
    if not category_to_delete:
        raise CATEGORY_NOT_FOUND
    return
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List

from src.dependencies import get_async_db
from src.services.auth_services import auth_access_token
from src.exceptions.http_errors import (
    CATEGORY_NOT_FOUND,
    CATEGORY_CREATION_FAILED,
    CATEGORY_ALREADY_EXISTS,
)
from src.services.categories_services import CategoriesServices
from src.schemas.categories_schema import CategoriesIn, CategoriesOut
from src.models.user_model import UserModel

categories = APIRouter()


@categories.post(
    "/", response_model=CategoriesOut, status_code=status.HTTP_201_CREATED
)
async def add_category(
    category: CategoriesIn,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_access_token),
):
    category_services = CategoriesServices(db)
    category_exists = await category_services.get_category_by_name(category.name, current_user)
    if category_exists:
        raise CATEGORY_ALREADY_EXISTS
    try:
        return await category_services.create_category(category, current_user)
    except IntegrityError:
        raise CATEGORY_CREATION_FAILED


@categories.get("/", response_model=List[CategoriesOut])
async def list_categories(
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_access_token),
):
    category_services = CategoriesServices(db)
    return await category_services.get_categories(current_user)


@categories.get("/{category_id}", response_model=CategoriesOut)
async def retrieve_category(
    category_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_access_token),
):
    category_services = CategoriesServices(db)
    category = await category_services.get_category(category_id, current_user)
    if not category:
        raise CATEGORY_NOT_FOUND
    return category


@categories.put("/{category_id}", response_model=CategoriesOut)
async def modify_category(
    category_id: int,
    category_in: CategoriesIn,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_access_token),
):
    category_services = CategoriesServices(db)
    category_exists = await category_services.get_category_by_name(category_in.name, current_user)
    if category_exists:
        raise CATEGORY_ALREADY_EXISTS
    try:
        updated_category = await category_services.update_category(
            category_id, category_in, current_user
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
    current_user: UserModel = Depends(auth_access_token),
):
    category_services = CategoriesServices(db)
    category_to_delete = await category_services.delete_category(category_id, current_user)
    if not category_to_delete:
        raise CATEGORY_NOT_FOUND
    return

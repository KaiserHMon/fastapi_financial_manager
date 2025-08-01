from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List

from src.dependencies import get_async_db
from src.services.auth_services import auth_access_token
from src.exceptions.http_errors import (
    EXPENSE_NOT_FOUND,
    EXPENSE_CREATION_FAILED,
    EXPENSE_UPDATE_FAILED,
)
from src.services.expenses_service import (
    create_expense,
    get_expenses,
    get_expense_by_id,
    update_expense,
    delete_expense,
)
from src.schemas.expenses_schema import ExpenseIn, ExpenseOut
from src.models.user_model import UserModel

expenses_router = APIRouter()


@expenses_router.post("/", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
async def add_expense(
    expense: ExpenseIn,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_access_token),
):
    try:
        return await create_expense(expense, current_user, db)
    except IntegrityError:  # Catches issues like invalid category_id
        raise EXPENSE_CREATION_FAILED


@expenses_router.get("/", response_model=List[ExpenseOut])
async def list_expenses(
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_access_token),
):

    return await get_expenses(current_user, db)


@expenses_router.get("/{expense_id}", response_model=ExpenseOut)
async def retrieve_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_access_token),
):
    expense = await get_expense_by_id(expense_id, current_user, db)
    if not expense:
        raise EXPENSE_NOT_FOUND
    return expense


@expenses_router.put("/{expense_id}", response_model=ExpenseOut)
async def modify_expense(
    expense_id: int,
    expense_in: ExpenseIn,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_access_token),
):
    try:
        updated_expense = await update_expense(expense_id, expense_in, current_user, db)
        if not updated_expense:
            raise EXPENSE_NOT_FOUND
        return updated_expense
    except IntegrityError:
        raise EXPENSE_UPDATE_FAILED


@expenses_router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_access_token),
):
    expense_to_delete = await delete_expense(expense_id, current_user, db)
    if not expense_to_delete:
        raise EXPENSE_NOT_FOUND
    return

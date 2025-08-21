from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import date
from fastapi_cache.decorator import cache

from ..dependencies import get_async_db
from ..services import auth_services, expenses_services
from ..exceptions.http_errors import (
    EXPENSE_NOT_FOUND,
    EXPENSE_CREATION_FAILED,
    EXPENSE_UPDATE_FAILED,
)
from ..schemas.expenses_schema import ExpenseIn, ExpenseOut
from ..models.user_model import UserModel

expenses = APIRouter()


@expenses.post("/", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
async def add_expense(
    expense: ExpenseIn,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_services.auth_access_token),
):
    try:
        return await expenses_services.create_expense(db, expense, current_user)
    except IntegrityError:
        raise EXPENSE_CREATION_FAILED


@expenses.get("/", response_model=List[ExpenseOut])
@cache(expire=3600)
async def list_expenses(
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_services.auth_access_token),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    skip: int = 0,
    limit: int = 100,
):
    return await expenses_services.get_expenses(
        db, current_user, from_date, to_date, skip, limit
    )


@expenses.get("/{expense_id}", response_model=ExpenseOut)
@cache(expire=3600)
async def retrieve_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_services.auth_access_token),
):
    expense = await expenses_services.get_expense_by_id(db, expense_id, current_user)
    if not expense:
        raise EXPENSE_NOT_FOUND
    return expense


@expenses.put("/{expense_id}", response_model=ExpenseOut)
async def modify_expense(
    expense_id: int,
    expense_in: ExpenseIn,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_services.auth_access_token),
):
    expense = await expenses_services.get_expense_by_id(db, expense_id, current_user)
    if not expense:
        raise EXPENSE_NOT_FOUND
    try:
        updated_expense = await expenses_services.update_expense(
            db, expense_id, expense_in, current_user
        )
        return updated_expense
    except IntegrityError:
        raise EXPENSE_UPDATE_FAILED


@expenses.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_services.auth_access_token),
):
    expense_to_delete = await expenses_services.delete_expense(
        db, expense_id, current_user
    )
    if not expense_to_delete:
        raise EXPENSE_NOT_FOUND
    return None
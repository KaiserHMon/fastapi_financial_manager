from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List

from dependencies import get_async_db
from services import auth_services, expenses_service
from exceptions.http_errors import (
    EXPENSE_NOT_FOUND,
    EXPENSE_CREATION_FAILED,
    EXPENSE_UPDATE_FAILED,
)
from schemas.expenses_schema import ExpenseIn, ExpenseOut
from models.user_model import UserModel

expenses = APIRouter()


@expenses.post("/", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
async def add_expense(
    expense: ExpenseIn,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_services.auth_access_token),
):
    try:
        return await expenses_service.create_expense(db, expense, current_user)
    except IntegrityError:  # Catches issues like invalid category_id
        raise EXPENSE_CREATION_FAILED


@expenses.get("/", response_model=List[ExpenseOut])
async def list_expenses(
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_services.auth_access_token),
):
    return await expenses_service.get_expenses(db, current_user)


@expenses.get("/{expense_id}", response_model=ExpenseOut)
async def retrieve_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_services.auth_access_token),
):
    expense = await expenses_service.get_expense_by_id(db, expense_id, current_user)
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
    expense = await expenses_service.get_expense_by_id(db, expense_id, current_user)
    if not expense:
        raise EXPENSE_NOT_FOUND
    try:
        updated_expense = await expenses_service.update_expense(
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
    expense_to_delete = await expenses_service.delete_expense(
        db, expense_id, current_user
    )
    if not expense_to_delete:
        raise EXPENSE_NOT_FOUND
    return
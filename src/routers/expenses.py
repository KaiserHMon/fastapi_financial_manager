from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.expenses_schema import ExpenseIn, ExpenseOut
from models.user_model import UserModel
from dependencies import get_async_db
from services.auth_services import auth_access_token
from services.expenses_service import (
    create_expense as create_expense_service,
    get_expenses as get_expenses_service,
    get_expense_by_id as get_expense_by_id_service,
    update_expense as update_expense_service,
    delete_expense as delete_expense_service
)

from exceptions.http_errors import (
    EXPENSE_NOT_FOUND,
    EXPENSE_CREATION_FAILED,
    EXPENSE_UPDATE_FAILED,
    SERVER_ERROR
)


expenses = APIRouter()

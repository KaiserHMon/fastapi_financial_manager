from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache

from ..dependencies import get_async_db
from ..services import auth_services, balance_services
from ..models.user_model import UserModel

balance = APIRouter()


@balance.get("/balance", summary="Get total balance")
@cache(expire=3600)
async def get_total_balance(
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_services.auth_access_token),
):
    balance = await balance_services.get_balance(db, current_user)
    return {"balance": balance}


@balance.get("/balance/incomes", summary="Get total incomes")
@cache(expire=3600)
async def get_total_incomes(
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_services.auth_access_token),
):
    balance_incomes = await balance_services.get_total_incomes(db, current_user)
    return {"balance": balance_incomes}


@balance.get("/balance/expenses", summary="Get total expenses")
@cache(expire=3600)
async def get_total_expenses(
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(auth_services.auth_access_token),
):
    balance_expenses = await balance_services.get_total_expenses(db, current_user)
    return {"balance": balance_expenses}


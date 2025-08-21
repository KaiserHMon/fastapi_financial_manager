from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from fastapi_cache.decorator import cache

from ..schemas.incomes_schema import IncomeIn, IncomeOut
from ..models.user_model import UserModel
from ..dependencies import get_async_db
from ..services import auth_services, incomes_services
from ..exceptions.http_errors import (
    INCOME_NOT_FOUND,
    INCOME_CREATION_FAILED,
    INCOME_UPDATE_FAILED,
    SERVER_ERROR,
)

incomes = APIRouter()


@incomes.post("/", response_model=IncomeOut)
async def create_income(
    income_in: IncomeIn,
    current_user: UserModel = Depends(auth_services.auth_access_token),
    db: AsyncSession = Depends(get_async_db),
):
    try:
        created_income = await incomes_services.create_income(
            db, income_in, current_user
        )
        if not created_income:
            raise INCOME_CREATION_FAILED
        return created_income
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        raise SERVER_ERROR


@incomes.get("/", response_model=list[IncomeOut])
@cache(expire=3600)
async def get_incomes(
    current_user: UserModel = Depends(auth_services.auth_access_token),
    db: AsyncSession = Depends(get_async_db),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    skip: int = 0,
    limit: int = 100,
):
    try:
        return await incomes_services.get_incomes(
            db, current_user, from_date, to_date, skip, limit
        )
    except Exception:
        raise SERVER_ERROR


@incomes.put("/{income_id}", response_model=IncomeOut)
async def update_income(
    income_id: int,
    income_in: IncomeIn,
    current_user: UserModel = Depends(auth_services.auth_access_token),
    db: AsyncSession = Depends(get_async_db),
):
    try:
        income = await incomes_services.get_income_by_id(db, income_id, current_user)
        if not income:
            raise INCOME_NOT_FOUND

        updated_income = await incomes_services.update_income(db, income, income_in)
        if not updated_income:
            raise INCOME_UPDATE_FAILED
        return updated_income
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        raise SERVER_ERROR


@incomes.delete("/{income_id}")
async def delete_income(
    income_id: int,
    current_user: UserModel = Depends(auth_services.auth_access_token),
    db: AsyncSession = Depends(get_async_db),
):
    try:
        income = await incomes_services.get_income_by_id(db, income_id, current_user)
        if not income:
            raise INCOME_NOT_FOUND

        await incomes_services.delete_income(db, income)
        return {"detail": "Income deleted successfully"}
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        raise SERVER_ERROR


@incomes.get("/{income_id}", response_model=IncomeOut)
@cache(expire=3600)
async def get_income_by_id(
    income_id: int,
    current_user: UserModel = Depends(auth_services.auth_access_token),
    db: AsyncSession = Depends(get_async_db),
):
    try:
        income = await incomes_services.get_income_by_id(db, income_id, current_user)
        if not income:
            raise INCOME_NOT_FOUND
        return income
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        raise SERVER_ERROR

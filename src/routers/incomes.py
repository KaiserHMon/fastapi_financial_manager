from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.incomes_schema import IncomeIn, IncomeOut
from models.user_model import UserModel
from dependencies import get_async_db
from services.auth_services import auth_access_token
from services.income_services import (
    create_income as create_income_service,
    get_incomes as get_incomes_service,
    get_income_by_id as get_income_by_id_service,
    update_income as update_income_service,
    delete_income as delete_income_service
)
from exceptions.http_errors import (
    INCOME_NOT_FOUND,
    INCOME_CREATION_FAILED,
    INCOME_UPDATE_FAILED,
    SERVER_ERROR
)


incomes = APIRouter()


@incomes.post("/incomes", response_model=IncomeOut)
async def create_income(
    income_in: IncomeIn,
    current_user: UserModel = Depends(auth_access_token),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        created_income = await create_income_service(income_in, current_user, db)
        if not created_income:
            raise INCOME_CREATION_FAILED
        return created_income
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        raise SERVER_ERROR


@incomes.get("/incomes", response_model=list[IncomeOut])
async def get_incomes(
    current_user: UserModel = Depends(auth_access_token),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        return await get_incomes_service(current_user, db)
    except Exception:
        raise SERVER_ERROR


@incomes.put("/incomes/{income_id}", response_model=IncomeOut)
async def update_income(
    income_id: int,
    income_in: IncomeIn,
    current_user: UserModel = Depends(auth_access_token),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        income = await get_income_by_id_service(income_id, current_user, db)
        if not income:
            raise INCOME_NOT_FOUND

        updated_income = await update_income_service(income, income_in, db)
        if not updated_income:
            raise INCOME_UPDATE_FAILED
        return updated_income
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        raise SERVER_ERROR


@incomes.delete("/incomes/{income_id}")
async def delete_income(
    income_id: int,
    current_user: UserModel = Depends(auth_access_token),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        income = await get_income_by_id_service(income_id, current_user, db)
        if not income:
            raise INCOME_NOT_FOUND

        await delete_income_service(income, db)
        return {"detail": "Income deleted successfully"}
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        raise SERVER_ERROR


@incomes.get("/incomes/{income_id}", response_model=IncomeOut)
async def get_income_by_id(
    income_id: int,
    current_user: UserModel = Depends(auth_access_token),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        income = await get_income_by_id_service(income_id, current_user, db)
        if not income:
            raise INCOME_NOT_FOUND
        return income
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        raise SERVER_ERROR


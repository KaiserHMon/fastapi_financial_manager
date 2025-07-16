from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from schemas.incomes_schema import IncomeIn, IncomeOut
from models.user_model import UserModel
from dependencies import get_async_db
from services.auth_services import auth_access_token
from services.income_services import (
    create_income, get_incomes, get_income_by_id, update_income, delete_income)


incomes = APIRouter()

@incomes.post("/incomes", response_model=IncomeOut)
async def create_income(income_in: IncomeIn,
                        current_user: UserModel = Depends(auth_access_token),
                        db: AsyncSession = Depends(get_async_db)):
    try:
        created_income = await create_income(income_in, current_user, db)
        return created_income
    except Exception as e:
        raise e


@incomes.get("/incomes", response_model=list[IncomeOut])
async def get_incomes(current_user: UserModel = Depends(auth_access_token),
                     db: AsyncSession = Depends(get_async_db)):
    try:
        incomes_list = await get_incomes(current_user, db)
        return incomes_list
    except Exception as e:
        raise e


@incomes.put("/incomes/{income_id}", response_model=IncomeOut)
async def update_income(income_id: int,
                        income_in: IncomeIn,
                        current_user: UserModel = Depends(auth_access_token),
                        db: AsyncSession = Depends(get_async_db)):
    try:
        income = await get_income_by_id(income_id, current_user, db)
        if not income:
            raise ##HTTPException(status_code=404, detail="Income not found")
        
        updated_income = await update_income(income, income_in, db)
        return updated_income
    except Exception as e:
        raise e
   
    
@incomes.delete("/incomes/{income_id}")
async def delete_income(income_id: int,
                        current_user: UserModel = Depends(auth_access_token),
                        db: AsyncSession = Depends(get_async_db)):
    try:
        income = await get_income_by_id(income_id, current_user, db)
        if not income:
            raise ##HTTPException(status_code=404, detail="Income not found")
        
        await delete_income(income, db)
        return {"detail": "Income deleted successfully"}
    except Exception as e:
        raise e
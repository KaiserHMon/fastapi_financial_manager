from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from schemas.incomes_schema import IncomeIn, IncomeOut
from models.user_model import UserModel
from dependencies import get_async_db
from services.auth_services import auth_access_token
from services.income_services import create_income


incomes = APIRouter()

@incomes.post("/incomes", response_model=IncomeOut)
async def create_income(income_in: IncomeIn,
                        current_user: UserModel = Depends(auth_access_token),
                        db: AsyncSession = Depends(get_async_db)):
    try:
        created_income = await create_income(income_in, current_user, db)
        return created_income
    except Exception as e:
        ##
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.incomes_schema import IncomeIn, IncomeOut
from models.user_model import UserModel
from dependencies import get_async_db
from services.auth_services import auth_access_token

categories = APIRouter()

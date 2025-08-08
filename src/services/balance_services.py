from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from ..models.user_model import UserModel
from ..models.incomes_model import IncomeModel
from ..models.expenses_model import ExpenseModel


async def get_total_incomes(db: AsyncSession, user: UserModel) -> float:
    total_incomes = await db.execute(
        select(func.sum(IncomeModel.amount)).where(IncomeModel.user_id == user.id)
    )
    return total_incomes.scalar_one_or_none() or 0.0


async def get_total_expenses(db: AsyncSession, user: UserModel) -> float:
    total_expenses = await db.execute(
        select(func.sum(ExpenseModel.amount)).where(ExpenseModel.user_id == user.id)
    )
    return total_expenses.scalar_one_or_none() or 0.0


async def get_balance(db: AsyncSession, user: UserModel) -> float:
    total_incomes = await get_total_incomes(db, user)
    total_expenses = await get_total_expenses(db, user)
    return total_incomes - total_expenses

from sqlalchemy.ext.asyncio import AsyncSession

from datetime import date

from ..schemas.history_schema import HistoryOut
from ..models.user_model import UserModel
from .incomes_services import get_incomes
from .expenses_services import get_expenses


async def get_history_entries(
    db: AsyncSession,
    user: UserModel,
    from_date: date | None,
    to_date: date | None,
    skip: int = 0,
    limit: int = 50
) -> list[HistoryOut]:
    incomes = await get_incomes(db, user, from_date, to_date)
    expenses = await get_expenses(db, user, from_date, to_date)

    history_data: list[HistoryOut] = []

    for income in incomes:
        history_data.append(HistoryOut(
            id=income.id,
            type="income",
            amount=income.amount,
            description=income.description,
            date=income.date,
            category=income.category.name if income.category else "Unknown"
        ))

    for expense in expenses:
        history_data.append(HistoryOut(
            id=expense.id,
            type="expense",
            amount=expense.amount,
            description=expense.description,
            date=expense.date,
            category=expense.category.name if expense.category else "Unknown"
        ))

    history_data.sort(key=lambda x: x.date, reverse=True)
    return history_data[skip : skip + limit]
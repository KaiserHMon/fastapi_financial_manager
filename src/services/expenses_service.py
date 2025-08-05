from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.user_model import UserModel
from ..models.expenses_model import ExpenseModel
from ..schemas.expenses_schema import ExpenseIn


async def create_expense(
    db: AsyncSession, expense: ExpenseIn, user: UserModel
) -> ExpenseModel:
    expenses_db = ExpenseModel(**expense.model_dump(), user_id=user.id)
    db.add(expenses_db)
    await db.commit()
    await db.refresh(expenses_db)
    return expenses_db


async def get_expenses(db: AsyncSession, user: UserModel):
    result = await db.execute(
        select(ExpenseModel).where(ExpenseModel.user_id == user.id)
    )
    return result.scalars().all()


async def get_expense_by_id(db: AsyncSession, expense_id: int, user: UserModel):
    result = await db.execute(
        select(ExpenseModel).where(
            ExpenseModel.id == expense_id, ExpenseModel.user_id == user.id
        )
    )
    return result.scalars().first()


async def update_expense(
    db: AsyncSession, expense_id: int, expense_in: ExpenseIn, user: UserModel
):
    expense_db = await get_expense_by_id(db, expense_id, user)
    if not expense_db:
        return None
    for key, value in expense_in.model_dump().items():
        setattr(expense_db, key, value)
    await db.commit()
    await db.refresh(expense_db)
    return expense_db


async def delete_expense(db: AsyncSession, expense_id: int, user: UserModel):
    expense_db = await get_expense_by_id(db, expense_id, user)
    if not expense_db:
        return None
    await db.delete(expense_db)
    await db.commit()
    return expense_db
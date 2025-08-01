from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.user_model import UserModel
from models.expenses_model import ExpenseModel
from schemas.expenses_schema import ExpenseIn


class ExpenseServices:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_expense(
        self, expense: ExpenseIn, user: UserModel
    ) -> ExpenseModel:
        expenses_db = ExpenseModel(**expense.model_dump(), user_id=user.id)
        self.db.add(expenses_db)
        await self.db.commit()
        await self.db.refresh(expenses_db)
        return expenses_db

    async def get_expenses(self, user: UserModel):
        result = await self.db.execute(
            select(ExpenseModel).where(ExpenseModel.user_id == user.id)
        )
        return result.scalars().all()

    async def get_expense_by_id(self, expense_id: int, user: UserModel):
        result = await self.db.execute(
            select(ExpenseModel).where(
                ExpenseModel.id == expense_id, ExpenseModel.user_id == user.id
            )
        )
        return result.scalars().first()

    async def update_expense(
        self, expense_id: int, expense_in: ExpenseIn, user: UserModel
    ):
        expense_db = await self.get_expense_by_id(expense_id, user)
        if not expense_db:
            return None
        for key, value in expense_in.model_dump().items():
            setattr(expense_db, key, value)
        await self.db.commit()
        await self.db.refresh(expense_db)
        return expense_db

    async def delete_expense(self, expense_id: int, user: UserModel):
        expense_db = await self.get_expense_by_id(expense_id, user)
        if not expense_db:
            return None
        await self.db.delete(expense_db)
        await self.db.commit()
        return expense_db

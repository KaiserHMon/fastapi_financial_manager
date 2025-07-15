from sqlalchemy.ext.asyncio import AsyncSession
from models.incomes_model import IncomeModel
from models.user_model import UserModel
from schemas.incomes_schema import IncomeIn, IncomeOut

async def create_income(income: IncomeIn, user: UserModel, db: AsyncSession) -> IncomeModel:
    income_db = IncomeModel(**income.model_dump(), user_id=user.id)
    db.add(income_db)
    await db.commit()
    await db.refresh(income_db)
    return income_db

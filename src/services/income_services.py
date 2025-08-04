from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.incomes_model import IncomeModel
from models.user_model import UserModel
from schemas.incomes_schema import IncomeIn


class IncomeServices:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_income(self, income: IncomeIn, user: UserModel) -> IncomeModel:
        income_db = IncomeModel(**income.model_dump(), user_id=user.id)
        self.db.add(income_db)
        await self.db.commit()
        await self.db.refresh(income_db)
        return income_db

    async def get_incomes(self, user: UserModel) -> list[IncomeModel]:
        incomes = await self.db.execute(
            select(IncomeModel).where(IncomeModel.user_id == user.id)
        )
        return incomes.scalars().all()

    async def get_income_by_id(
        self, income_id: int, user: UserModel
    ) -> IncomeModel | None:
        income = await self.db.execute(
            select(IncomeModel).where(
                IncomeModel.id == income_id, IncomeModel.user_id == user.id
            )
        )
        return income.scalar_one_or_none()

    async def update_income(
        self, income: IncomeModel, income_in: IncomeIn
    ) -> IncomeModel:
        for field, value in income_in.model_dump(exclude_unset=True).items():
            setattr(income, field, value)

        self.db.add(income)
        await self.db.commit()
        await self.db.refresh(income)
        return income

    async def delete_income(self, income: IncomeModel):
        await self.db.delete(income)
        await self.db.commit()
        return None

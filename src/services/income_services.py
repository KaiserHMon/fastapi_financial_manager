from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.incomes_model import IncomeModel
from models.user_model import UserModel
from schemas.incomes_schema import IncomeIn


async def create_income(
    db: AsyncSession, income: IncomeIn, user: UserModel
) -> IncomeModel:
    income_db = IncomeModel(**income.model_dump(), user_id=user.id)
    db.add(income_db)
    await db.commit()
    await db.refresh(income_db)
    return income_db


async def get_incomes(db: AsyncSession, user: UserModel) -> list[IncomeModel]:
    incomes = await db.execute(
        select(IncomeModel).where(IncomeModel.user_id == user.id)
    )
    return incomes.scalars().all()


async def get_income_by_id(
    db: AsyncSession, income_id: int, user: UserModel
) -> IncomeModel | None:
    income = await db.execute(
        select(IncomeModel).where(
            IncomeModel.id == income_id, IncomeModel.user_id == user.id
        )
    )
    return income.scalar_one_or_none()


async def update_income(
    db: AsyncSession, income: IncomeModel, income_in: IncomeIn
) -> IncomeModel:
    for field, value in income_in.model_dump(exclude_unset=True).items():
        setattr(income, field, value)

    db.add(income)
    await db.commit()
    await db.refresh(income)
    return income


async def delete_income(db: AsyncSession, income: IncomeModel):
    await db.delete(income)
    await db.commit()
    return None
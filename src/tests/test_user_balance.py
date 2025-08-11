import uuid
from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user_model import UserModel
from ..models.incomes_model import IncomeModel
from ..models.expenses_model import ExpenseModel
from ..models.categories_model import CategoryModel


@pytest.mark.asyncio
async def test_get_balance(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: UserModel,
    access_token: str,
):
    income_category = CategoryModel(
        name=f"income_category_{uuid.uuid4()}", type="income", user_id=test_user.id
    )
    expense_category = CategoryModel(
        name=f"expense_category_{uuid.uuid4()}", type="expense", user_id=test_user.id
    )
    db_session.add_all([income_category, expense_category])
    await db_session.commit()
    await db_session.refresh(income_category)
    await db_session.refresh(expense_category)

    income = IncomeModel(
        amount=100.0,
        description="Income 2",
        date=date.today(),
        user_id=test_user.id,
        category_id=income_category.id,
    )
    expense = ExpenseModel(
        amount=25.0,
        description="Expense 2",
        date=date.today(),
        user_id=test_user.id,
        category_id=expense_category.id,
    )
    db_session.add_all([income, expense])
    await db_session.commit()

    headers = {"Authorization": f"Bearer {access_token}"}
    response = await async_client.get("/user/balance", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"balance": 75.0}


@pytest.mark.asyncio
async def test_get_total_incomes(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: UserModel,
    access_token: str,
):
    income_category = CategoryModel(
        name=f"income_category_{uuid.uuid4()}", type="income", user_id=test_user.id
    )
    db_session.add(income_category)
    await db_session.commit()
    await db_session.refresh(income_category)

    income = IncomeModel(
        amount=100.0,
        description="Income 1",
        date=date.today(),
        user_id=test_user.id,
        category_id=income_category.id,
    )
    db_session.add(income)
    await db_session.commit()

    headers = {"Authorization": f"Bearer {access_token}"}
    response = await async_client.get("/user/balance/incomes", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"balance": 100.0}


@pytest.mark.asyncio
async def test_get_total_expenses(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: UserModel,
    access_token: str,
):
    expense_category = CategoryModel(
        name=f"expense_category_{uuid.uuid4()}", type="expense", user_id=test_user.id
    )
    db_session.add(expense_category)
    await db_session.commit()
    await db_session.refresh(expense_category)

    expense = ExpenseModel(
        amount=25.0,
        description="Expense 1",
        date=date.today(),
        user_id=test_user.id,
        category_id=expense_category.id,
    )
    db_session.add(expense)
    await db_session.commit()

    headers = {"Authorization": f"Bearer {access_token}"}
    response = await async_client.get("/user/balance/expenses", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"balance": 25.0}
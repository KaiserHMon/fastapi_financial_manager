from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload


from ..models.categories_model import CategoryModel
from ..models.user_model import UserModel
from ..schemas.categories_schema import CategoriesIn


async def get_category_by_name(
    db: AsyncSession, category_name: str, user: UserModel
) -> CategoryModel | None:
    result = await db.execute(
        select(CategoryModel).where(
            CategoryModel.name == category_name, CategoryModel.user_id == user.id
        )
    )
    return result.scalars().first()


async def create_category(db: AsyncSession, category: CategoriesIn, user: UserModel):
    new_category = CategoryModel(**category.model_dump(), user_id=user.id)
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    return new_category


async def get_categories(db: AsyncSession, user: UserModel):
    result = await db.execute(
        select(CategoryModel)
        .where(CategoryModel.user_id == user.id)
        .options(joinedload(CategoryModel.user))
    )
    return result.scalars().unique().all()


async def get_category(db: AsyncSession, category_id: int, user: UserModel):
    result = await db.execute(
        select(CategoryModel).where(
            CategoryModel.id == category_id, CategoryModel.user_id == user.id
        )
    )
    return result.scalars().first()


async def update_category(
    db: AsyncSession, category_id: int, category_data: CategoriesIn, user: UserModel
):
    category = await get_category(db, category_id, user)
    if not category:
        return None

    for key, value in category_data.model_dump().items():
        setattr(category, key, value)
    await db.commit()
    await db.refresh(category)
    return category


async def delete_category(db: AsyncSession, category_id: int, user: UserModel):
    category = await get_category(db, category_id, user)
    if not category:
        return None
    await db.delete(category)
    await db.commit()
    return True
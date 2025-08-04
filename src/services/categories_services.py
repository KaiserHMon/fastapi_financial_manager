from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload


from models.categories_model import CategoryModel
from models.user_model import UserModel
from schemas.categories_schema import CategoriesIn


class CategoriesServices:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_category_by_name(self, category_name: str, user: UserModel) -> CategoryModel | None:
        result = await self.db.execute(
            select(CategoryModel).where(
                CategoryModel.name == category_name, CategoryModel.user_id == user.id
            )
        )
        return result.scalars().first()

    async def create_category(self, category: CategoriesIn, user: UserModel):
        new_category = CategoryModel(**category.model_dump(), user_id=user.id)
        self.db.add(new_category)
        await self.db.commit()
        await self.db.refresh(new_category)
        return new_category


    async def get_categories(self, user: UserModel):
        result = await self.db.execute(
            select(CategoryModel)
            .where(CategoryModel.user_id == user.id)
            .options(joinedload(CategoryModel.user))
        )
        return result.scalars().unique().all()


    async def get_category(self, category_id: int, user: UserModel):
        result = await self.db.execute(
            select(CategoryModel).where(
                CategoryModel.id == category_id, CategoryModel.user_id == user.id
            )
        )
        return result.scalars().first()


    async def update_category(
        self, category_id: int, category_data: CategoriesIn, user: UserModel
    ):
        category = await self.get_category(category_id, user)
        if not category:
            return None

        for key, value in category_data.model_dump().items():
            setattr(category, key, value)
        await self.db.commit()
        await self.db.refresh(category)
        return category


    async def delete_category(self, category_id: int, user: UserModel):
        category = await self.get_category(category_id, user)
        if not category:
            return None
        await self.db.delete(category)
        await self.db.commit()
        return True


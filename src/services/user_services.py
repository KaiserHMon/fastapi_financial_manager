from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user_model import UserModel
from schemas.user_schema import UserIn, UserBase
from services.password_services import get_password_hash


class UserServices:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(self, username: str) -> UserModel | None:
        user = await self.db.execute(
            select(UserModel).where(UserModel.username == username)
        )
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> UserModel | None:
        user = await self.db.execute(select(UserModel).where(UserModel.email == email))
        return user.scalar_one_or_none()

    async def create_user(self, user: UserIn) -> UserModel:
        hashed_password = get_password_hash(user.password)
        user_db = UserModel(
            **user.model_dump(exclude={"password"}), password=hashed_password
        )
        self.db.add(user_db)
        await self.db.commit()
        await self.db.refresh(user_db)
        return user_db

    async def update_user(self, user: UserModel, user_in: UserBase) -> UserModel:
        for field, value in user_in.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user: UserModel) -> None:
        await self.db.delete(user)
        await self.db.commit()
        return None

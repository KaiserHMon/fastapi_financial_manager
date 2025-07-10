from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user_model import UserModel
from schemas.user_schema import UserIn

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"] , deprecated="auto") # Password hashing context


async def get_user(username: str, db: AsyncSession) -> UserModel | None:
        user = await db.execute(select(UserModel).where(UserModel.username == username))
        return user.scalar_one_or_none()

from schemas.user_schema import UserIn


async def create_user(user: UserIn, db: AsyncSession) -> UserModel:
        hashed_password = pwd_context.hash(user.password)
        user_db = UserModel(**user.model_dump(exclude={"password"}), password=hashed_password)
        db.add(user_db)
        await db.commit()
        return user_db
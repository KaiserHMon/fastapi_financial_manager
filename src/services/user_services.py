from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user_model import UserModel

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"] , deprecated="auto") # Password hashing context


async def get_user(username: str, db: AsyncSession) -> UserModel | None:
        user = await db.execute(select(UserModel).where(UserModel.username == username))
        return user.scalar_one_or_none()

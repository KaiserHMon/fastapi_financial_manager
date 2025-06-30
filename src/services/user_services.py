from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user_model import UserModel
from schemas.user_schema import UserIn
from dependencies import get_async_db

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"] , deprecated="auto") # Password hashing context

async def get_user(username: str, db: AsyncSession) -> UserModel | None:
        user = await db.execute(select(UserModel).where(UserModel.username == username))
        return user.scalar_one_or_none


def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

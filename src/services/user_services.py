from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user_model import UserModel
from schemas.user_schema import UserIn, UserBase

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"] , deprecated="auto") # Password hashing context


async def get_user(username: str, db: AsyncSession) -> UserModel | None:
        user = await db.execute(select(UserModel).where(UserModel.username == username))
        return user.scalar_one_or_none()

async def get_user_by_email(email: str, db: AsyncSession) -> UserModel | None:
        user = await db.execute(select(UserModel).where(UserModel.email == email))
        return user.scalar_one_or_none()

async def create_user(user: UserIn, db: AsyncSession) -> UserModel:
        hashed_password = pwd_context.hash(user.password)
        user_db = UserModel(**user.model_dump(exclude={"password"}), password=hashed_password)
        db.add(user_db)
        await db.commit()
        await db.refresh(user_db)
        return user_db

async def update_user(user: UserModel, user_in: UserBase, db: AsyncSession) -> UserModel:
        for field, value in user_in.model_dump(exclude_unset=True).items():
                setattr(user, field, value)
    
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

async def delete_user(user: UserModel, db: AsyncSession) -> None:
        await db.delete(user)
        await db.commit()
        return None
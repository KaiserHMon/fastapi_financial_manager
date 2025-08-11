from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.user_model import UserModel
from ..schemas.user_schema import UserIn, UserUpdateProfile
from ..services.password_services import get_password_hash


async def get_user(db: AsyncSession, username: str) -> UserModel | None:
    user = await db.execute(select(UserModel).where(UserModel.username == username))
    return user.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> UserModel | None:
    user = await db.execute(select(UserModel).where(UserModel.email == email))
    return user.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserIn) -> UserModel:
    hashed_password = get_password_hash(user.password)
    user_db = UserModel(**user.model_dump(exclude={"password"}), password=hashed_password)
    db.add(user_db)
    await db.commit()
    await db.refresh(user_db)
    return user_db


async def update_user(db: AsyncSession, user: UserModel, user_in: UserUpdateProfile) -> UserModel:
    if user_in.full_name is not None:
        user.full_name = user_in.full_name

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: UserModel) -> None:
    await db.delete(user)
    await db.commit()
    return None


async def get_all_users(db: AsyncSession) -> list[UserModel]:
    users = await db.execute(select(UserModel))
    return users.scalars().all()


async def get_user_by_id(db: AsyncSession, user_id: int) -> UserModel | None:
    user = await db.execute(select(UserModel).where(UserModel.id == user_id))
    return user.scalar_one_or_none()
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from datetime import datetime

from .models.token_denylist_model import TokenDenylist
from .dependencies import get_async_db


async def cleanup_expired_tokens():
    """Deletes expired tokens from the denylist."""
    db: AsyncSession = get_async_db().__anext__()
    async with db as session:
        await session.execute(
            delete(TokenDenylist).where(TokenDenylist.exp < datetime.utcnow())
        )
        await session.commit()
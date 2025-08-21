from fastapi import FastAPI
import uvicorn
from fastapi_utils.tasks import repeat_every
from contextlib import asynccontextmanager
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from .config.settings import settings
from .routers.auth import auth
from .routers.user import user
from .routers.incomes import incomes
from .routers.categories import categories
from .routers.expenses import expenses
from .routers.user_balance import balance
from .tasks import cleanup_expired_tokens

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    redis = aioredis.from_url(settings.REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    @repeat_every(seconds=60 * 60 * 24)  # 24 hours
    async def schedule_cleanup():
        await cleanup_expired_tokens()
    await schedule_cleanup() # Run once at startup
    yield
    # Shutdown


app = FastAPI(title="InFinity Managment", version="0.1.0", lifespan=lifespan)

app.include_router(auth, prefix="/auth", tags=["Auth"])
app.include_router(balance, prefix="/user", tags=["Balance"])
app.include_router(user, prefix="/user", tags=["User"])
app.include_router(incomes, prefix="/incomes", tags=["Incomes"])
app.include_router(categories, prefix="/categories", tags=["Categories"])
app.include_router(expenses, prefix="/expenses", tags=["Expenses"])


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    uvicorn.run("main:app", port=8080, host='0.0.0.0', reload=True)
    # http://localhost:8080/
    # poetry run uvicorn src.main:app --reload


__init__ = "src.main"
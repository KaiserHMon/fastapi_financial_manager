from fastapi import FastAPI
import uvicorn
from fastapi_utils.tasks import repeat_every
from contextlib import asynccontextmanager

from routers.auth import auth
from routers.user import user
from routers.incomes import incomes
from routers.categories import categories
from tasks import cleanup_expired_tokens

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    @repeat_every(seconds=60 * 60 * 24)  # 24 hours
    async def schedule_cleanup():
        await cleanup_expired_tokens()
    await schedule_cleanup() # Run once at startup
    yield
    # Shutdown


app = FastAPI(title="InFinity Managment", version="0.1.0", lifespan=lifespan)

app.include_router(auth)
app.include_router(user)
app.include_router(incomes)
app.include_router(categories)


@app.get("/", tags=["Prueba"])
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    uvicorn.run("main:app", port=8080, host='0.0.0.0', reload=True)
    # http://localhost:8080/


__init__ = "src.main"
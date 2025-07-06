from fastapi import FastAPI
import uvicorn
from fastapi_utils.tasks import repeat_every

from routers.auth import auth
from tasks import cleanup_expired_tokens


app = FastAPI(title="InFinity Managment", version="0.1.0")

app.include_router(auth)

@app.on_event("startup")
@repeat_every(seconds=60 * 60 * 24)  # 24 hours
async def schedule_cleanup():
    await cleanup_expired_tokens()

@app.get("/", tags=["Prueba"])
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    uvicorn.run("main:app", port=8080, host='0.0.0.0', reload=True)
    # http://localhost:8080/
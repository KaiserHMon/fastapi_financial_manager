from fastapi import FastAPI
import uvicorn

app = FastAPI(title="InFinity Managment", version="0.1.0")

@app.get("/", tags=["Prueba"])
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    uvicorn.run("main:app", port=8080, host='0.0.0.0', reload=True)
    # http://localhost:8080/
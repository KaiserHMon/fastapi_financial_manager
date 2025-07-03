import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from src.main import app
from src.models.user_model import UserModel
from src.dependencies import get_async_db
from src.services.password_services import get_password_hash

# Configure the test database
DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Dependency override for tests
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_async_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(UserModel.metadata.create_all)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        await db.close()
        async with engine.begin() as conn:
            await conn.run_sync(UserModel.metadata.drop_all)

@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession):
    user = UserModel(
        username="testuser",
        email="testuser@example.com",
        password=get_password_hash("password"),
    )
    db_session.add(user)
    await db_session.commit()
    return user

def test_login_for_access_token(test_user):
    response = client.post("/login", data={"username": "testuser", "password": "password"})
    assert response.status_code == 200
    json_response = response.json()
    assert "access_token" in json_response
    assert json_response["token_type"] == "bearer"

def test_login_for_access_token_user_not_found():
    response = client.post("/login", data={"username": "nonexistentuser", "password": "password"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

def test_login_for_access_token_wrong_password(test_user):
    response = client.post("/login", data={"username": "testuser", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Wrong password"}

import pytest
import pytest_asyncio
from httpx import AsyncClient
from asyncio import current_task
import starlette.status as status
from sqlalchemy.ext.asyncio import async_scoped_session, create_async_engine, AsyncSession, async_sessionmaker

from api.main import app
from api.database import get, Base


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    async_engine = create_async_engine('sqlite+aiosqlite:///:memory:', echo=True)
    async_session = async_scoped_session(
        async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=async_engine
        ), scopefunc=current_task
    )

    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    async def override_get() -> AsyncSession:
        async with async_session() as session:
            yield session

    app.dependency_overrides[get] = override_get

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_task(async_client):
    response = await async_client.post("/tasks", json={"title": "テストタスク"})
    assert response.status_code == status.HTTP_200_OK
    response_obj = response.json()
    assert response_obj["title"] == "テストタスク"

    response = await async_client.get("/tasks")
    assert response.status_code == status.HTTP_200_OK
    response_obj = response.json()
    assert len(response_obj) == 1
    assert response_obj[0]["title"] == "テストタスク"
    assert response_obj[0]["done"] is False


@pytest.mark.asyncio
async def test_done(async_client):
    response = await async_client.post("/tasks", json={"title": "テストタスク"})
    assert response.status_code == status.HTTP_200_OK
    response_obj = response.json()
    assert response_obj["title"] == "テストタスク"

    response = await async_client.put("/tasks/1/done")
    assert response.status_code == status.HTTP_200_OK

    response = await async_client.put("/tasks/1/done")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = await async_client.delete("/tasks/1/done")
    assert response.status_code == status.HTTP_200_OK

    response = await async_client.delete("/tasks/1/done")
    assert response.status_code == status.HTTP_404_NOT_FOUND

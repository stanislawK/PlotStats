import asyncio
from typing import Generator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.pool import StaticPool
import httpx
from typing import AsyncIterator

from api.main import create_app
from api.database import get_async_session

examples: dict[str, dict[str, str | int]] = {
    "category": {"name": "Plot"},
    "search": {
        "location": "London",
        "distance_radius": 10,
        "coordinates": "neLat: 50.474910540541,neLng: 16.720976750824,swLat: 50.393829459459,swLng: 16.593683249176",  # noqa
        "from_price": 10000,
        "to_price": 100000,
        "from_surface": 0,
        "to_surface": 5000,
    },
    "user": {"email": "john@test.com"},
    "estate": {
        "title": "Some great deal",
        "street": "Glowna 31",
        "city": "Pcim Dolny",
        "province": "Podlasie",
        "location": "Podlasie, Pcim Dolny, Glowna 31",
        "url": "www.test.com",
    },
    "price": {
        "price": 100000,
        "price_per_square_meter": 100,
        "area_in_square_meters": 10000,
        "terrain_area_in_square_meters": 10000,
    },
}


@pytest.fixture(autouse=True)
def app():
    _app = create_app()
    yield _app


@pytest_asyncio.fixture
async def _db_session() -> Generator[AsyncSession, None, None]:
    """Create temporary database for tests"""
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session() as s:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        yield s

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def client(app, _db_session) -> AsyncIterator[httpx.AsyncClient]:
    async def override_db():
        async with _db_session as s:
            yield s

    app.dependency_overrides[get_async_session] = override_db
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:  # noqa: indirect usage
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

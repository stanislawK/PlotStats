from typing import Any, AsyncIterator, Generator

import fakeredis
import httpx
import pytest
import pytest_asyncio
from _pytest.logging import LogCaptureFixture
from fastapi import FastAPI
from loguru import logger
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.pool import StaticPool

from api.database import get_async_session
from api.main import create_app
from api.models.category import Category
from api.models.user import User
from api.utils.jwt import create_jwt_token
from api.utils.user import get_password_hash

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
        "url": "https://www.test.io/test",
    },
    "user": {"email": "john@test.com", "password": "testpass"},
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
def app() -> Generator[FastAPI, None, None]:
    _app = create_app()
    yield _app


@pytest.fixture
def cache() -> Generator[fakeredis.FakeRedis, None, None]:
    cache = fakeredis.FakeRedis(decode_responses=True)  # type:ignore
    yield cache


@pytest_asyncio.fixture
async def _db_session() -> AsyncIterator[AsyncSession]:
    """Create temporary database for tests"""
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False  # type: ignore
    )
    async with session() as s:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        yield s

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def caplog(caplog: LogCaptureFixture) -> Generator[LogCaptureFixture, None, None]:
    handler_id = logger.add(
        caplog.handler,
        format="{message}",
        level=0,
        filter=lambda record: record["level"].no >= caplog.handler.level,
        enqueue=False,
    )
    yield caplog
    logger.remove(handler_id)


@pytest.fixture(scope="session")
def celery_config() -> dict[str, str]:
    return {"broker_url": "redis://", "result_backend": "redis://"}


@pytest.fixture
async def client(
    app: FastAPI,
    _db_session: AsyncSession,
    caplog: LogCaptureFixture,
    mocker: MockerFixture,
    cache: fakeredis.FakeRedis,
    celery_config: dict[str, str],
) -> AsyncIterator[httpx.AsyncClient]:
    async def override_db() -> AsyncIterator[AsyncSession]:
        async with _db_session as s:
            yield s

    app.dependency_overrides[get_async_session] = override_db

    mocker.patch("api.utils.fetching.cache", cache)
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture
async def authenticated_client(
    app: FastAPI,
    _db_session: AsyncSession,
    add_user: User,
    caplog: LogCaptureFixture,
    mocker: MockerFixture,
    cache: fakeredis.FakeRedis,
    celery_config: dict[str, str],
) -> AsyncIterator[httpx.AsyncClient]:
    async def override_db() -> AsyncIterator[AsyncSession]:
        async with _db_session as s:
            yield s

    app.dependency_overrides[get_async_session] = override_db

    mocker.patch("api.utils.fetching.cache", cache)
    token = create_jwt_token(subject=str(add_user.id), fresh=True, token_type="access")
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        client.headers.update({"Authorization": f"Bearer {token}"})
        yield client


@pytest.fixture
async def admin_client(
    app: FastAPI,
    _db_session: AsyncSession,
    add_admin: User,
    caplog: LogCaptureFixture,
    mocker: MockerFixture,
    cache: fakeredis.FakeRedis,
    celery_config: dict[str, str],
) -> AsyncIterator[httpx.AsyncClient]:
    async def override_db() -> AsyncIterator[AsyncSession]:
        async with _db_session as s:
            yield s

    app.dependency_overrides[get_async_session] = override_db

    mocker.patch("api.utils.fetching.cache", cache)
    token = create_jwt_token(subject=str(add_admin.id), fresh=True, token_type="access")
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        client.headers.update({"Authorization": f"Bearer {token}"})
        yield client


@pytest.fixture
async def add_user(_db_session: AsyncSession) -> User:
    user = User(
        email=examples["user"]["email"],
        password=get_password_hash(examples["user"]["password"]),  # type: ignore
        is_active=True,
    )
    _db_session.add(user)
    await _db_session.commit()
    return user


@pytest.fixture
async def add_admin(_db_session: AsyncSession) -> User:
    user = User(
        email=examples["user"]["email"],
        password=get_password_hash(examples["user"]["password"]),  # type: ignore
        is_active=True,
        roles=["admin"],
    )
    _db_session.add(user)
    await _db_session.commit()
    return user


@pytest.fixture
async def add_category(_db_session: AsyncSession) -> Category:
    category = Category(**examples["category"])
    _db_session.add(category)
    await _db_session.commit()
    return category


class MockAioJSONResponse:
    def __init__(self, json: dict[str, Any], status: int):
        self._json = json
        self.status = status

    async def json(self) -> dict[str, Any]:
        return self._json

    async def __aexit__(self, exc_type, exc, tb):  # type: ignore
        pass

    async def __aenter__(self):  # type: ignore
        return self


class MockAioTextResponse:
    def __init__(self, text: str, status: int):
        self._text = text
        self.status = status

    async def text(self) -> str:
        return self._text

    async def __aexit__(self, exc_type, exc, tb):  # type: ignore
        pass

    async def __aenter__(self):  # type: ignore
        return self

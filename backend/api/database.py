from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from .settings import settings

async_engine = create_async_engine(settings.db_uri, echo=True, future=True)


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        async_session = sessionmaker(
            bind=async_engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.close()


# async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
#     async_session = sessionmaker(
#         bind=async_engine, class_=AsyncSession, expire_on_commit=False
#     )
#     async with async_session() as session:
#         yield session

import strawberry
from sqlmodel import select
from strawberry.types import Info

from api.database import get_async_session
from api.models.category import Category
from api.types.category import CategoryType


async def resolve_categories(root, info: Info) -> list[CategoryType]:
    async with get_async_session() as session:
        query = select(Category)
        categories_db = (await session.execute(query)).scalars().all()
    return [CategoryType(name=c.name) for c in categories_db]


# async def resolve_categories(root, info: Info) -> list[CategoryType]:
#     async for session in get_async_session():
#         query = select(Category)
#         categories_db = (await session.execute(query)).scalars().all()
#     return [CategoryType(name=c.name) for c in categories_db]


@strawberry.type
class Query:
    categories: list[CategoryType] = strawberry.field(resolver=resolve_categories)

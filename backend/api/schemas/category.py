import strawberry
from sqlmodel import select
from strawberry.types import Info
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.category import Category
from api.types.category import CategoryType


async def resolve_categories(root, info: Info) -> list[CategoryType]:
    session: AsyncSession = info.context["session"]
    query = select(Category)
    categories_db = (await session.execute(query)).scalars().all()
    return [CategoryType(name=c.name) for c in categories_db]


@strawberry.type
class Query:
    categories: list[CategoryType] = strawberry.field(resolver=resolve_categories)

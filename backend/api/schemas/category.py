from typing import Any

import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from strawberry.types import Info

from api.models.category import Category
from api.types.category import CategoryType


async def resolve_categories(root: Any, info: Info[Any, Any]) -> list[CategoryType]:
    session: AsyncSession = info.context["session"]
    query = select(Category)
    categories_db = (await session.execute(query)).scalars().all()
    return [CategoryType(name=c.name) for c in categories_db]  # type: ignore


@strawberry.type
class Query:
    categories: list[CategoryType] = strawberry.field(resolver=resolve_categories)

from typing import Any

import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from strawberry.types import Info

from api.models.category import Category
from api.types.category import (
    CategoryExistsError,
    CategoryType,
    CreateCategoryResponse,
    CreateUserInput,
    convert_category_from_db,
)


async def resolve_categories(root: Any, info: Info[Any, Any]) -> list[CategoryType]:
    session: AsyncSession = info.context["session"]
    query = select(Category)
    categories_db = (await session.execute(query)).scalars().all()
    return [convert_category_from_db(cat) for cat in categories_db]


@strawberry.type
class Query:
    categories: list[CategoryType] = strawberry.field(resolver=resolve_categories)


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_category(
        self, info: Info[Any, Any], input: CreateUserInput
    ) -> CreateCategoryResponse:  # type: ignore
        session: AsyncSession = info.context["session"]
        if (
            await session.execute(select(Category).where(Category.name == input.name))
        ).scalar():
            return CategoryExistsError()
        category = Category(name=input.name)
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return convert_category_from_db(category)

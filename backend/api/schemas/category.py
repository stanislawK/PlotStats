from typing import Any

import strawberry
from loguru import logger
from pydantic import ValidationError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from strawberry.types import Info

from api.models.category import Category
from api.permissions import IsAdminUser, IsAuthenticated
from api.types.category import (
    CategoryExistsError,
    CategoryType,
    CreateCategoryResponse,
    CreateUserInput,
    convert_category_from_db,
)
from api.types.general import InputValidationError


async def resolve_categories(root: Any, info: Info[Any, Any]) -> list[CategoryType]:
    session: AsyncSession = info.context["session"]
    query = select(Category)
    categories_db = (await session.exec(query)).all()
    return [convert_category_from_db(cat) for cat in categories_db]


@strawberry.type
class Query:
    categories: list[CategoryType] = strawberry.field(
        resolver=resolve_categories, permission_classes=[IsAuthenticated]
    )


@strawberry.type
class Mutation:
    @strawberry.mutation(permission_classes=[IsAdminUser])  # type: ignore
    async def create_category(
        self, info: Info[Any, Any], input: CreateUserInput
    ) -> CreateCategoryResponse:
        # This will run pydantic's validation
        try:
            data = input.to_pydantic()
        except ValidationError as error:
            return InputValidationError(message=str(error))
        session: AsyncSession = info.context["session"]
        if (
            await session.exec(select(Category).where(Category.name == data.name))
        ).first():
            return CategoryExistsError()
        category = Category(name=data.name)
        logger.info(f"Creating new category {data.name}")
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return convert_category_from_db(category)

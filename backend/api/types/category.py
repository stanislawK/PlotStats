from typing import Annotated, Union

import strawberry
from pydantic import BaseModel, StringConstraints, field_validator

from api.models.category import Category
from api.types.general import Error, InputValidationError


@strawberry.experimental.pydantic.type(Category)
class CategoryType:
    name: strawberry.auto


class PydanticCategoryUserInput(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1, max_length=32)]

    @field_validator("name")
    @classmethod
    @classmethod
    def capitalize_first_letter(cls, value: str) -> str:
        return value.title()


@strawberry.experimental.pydantic.input(model=PydanticCategoryUserInput)
class CreateUserInput:
    name: strawberry.auto


@strawberry.type
class CategoryExistsError(Error):
    message: str = "Category already exists"


CreateCategoryResponse = Annotated[
    Union[CategoryType, CategoryExistsError, InputValidationError],
    strawberry.union("CreateCategoryResponse"),
]


def convert_category_from_db(db_category: Category) -> "CategoryType":
    return CategoryType(name=db_category.name)

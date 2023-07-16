import strawberry
from pydantic import BaseModel, constr, validator

from api.models.category import Category
from api.types.general import Error, InputValidationError


@strawberry.experimental.pydantic.type(Category, fields=["name"])
class CategoryType:
    pass


class PydanticCategoryUserInput(BaseModel):
    name: constr(min_length=1, max_length=32)  # type: ignore

    @validator("name")
    @classmethod
    def capitalize_first_letter(cls, value: str) -> str:
        return value.title()


@strawberry.experimental.pydantic.input(
    model=PydanticCategoryUserInput, fields=["name"]
)
class CreateUserInput:
    pass


@strawberry.type
class CategoryExistsError(Error):
    message: str = "Category already exists"


CreateCategoryResponse = strawberry.union(
    "CreateCategoryResponse", (CategoryType, CategoryExistsError, InputValidationError)
)


def convert_category_from_db(db_category: Category) -> "CategoryType":
    return CategoryType(name=db_category.name)

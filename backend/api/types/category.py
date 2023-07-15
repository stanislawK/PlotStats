import strawberry

from api.models.category import Category
from api.types.general import Error


@strawberry.experimental.pydantic.type(Category, fields=["name"])
class CategoryType:
    pass


@strawberry.experimental.pydantic.input(model=Category)
class CreateUserInput:
    name: str


@strawberry.type
class CategoryExistsError(Error):
    message: str = "Category already exists"


CreateCategoryResponse = strawberry.union(
    "CreateCategoryResponse", (CategoryType, CategoryExistsError)
)


def convert_category_from_db(db_category: Category) -> "CategoryType":
    return CategoryType(name=db_category.name)  # type: ignore

import strawberry

from api.models.estate import Estate


@strawberry.experimental.pydantic.type(
    Estate,
)
class EstateType:
    title: strawberry.auto
    street: strawberry.auto
    city: strawberry.auto
    province: strawberry.auto
    location: strawberry.auto
    date_created: strawberry.auto
    url: strawberry.auto

import strawberry

from api.models.estate import Estate


@strawberry.experimental.pydantic.type(
    Estate,
    fields=["title", "street", "city", "province", "location", "date_created", "url"],
)
class EstateType:
    pass

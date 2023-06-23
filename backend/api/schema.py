import strawberry

import api.schemas.category


@strawberry.type
class Query(api.schemas.category.Query):
    pass


schema = strawberry.Schema(Query)

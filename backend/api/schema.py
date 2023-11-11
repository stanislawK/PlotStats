import strawberry

import api.schemas.category
import api.schemas.scan
import api.schemas.search
import api.schemas.search_event


@strawberry.type
class Query(
    api.schemas.category.Query, api.schemas.search_event.Query, api.schemas.search.Query
):
    pass


@strawberry.type
class Mutation(api.schemas.category.Mutation, api.schemas.scan.Mutation):
    pass


schema = strawberry.Schema(Query, Mutation)

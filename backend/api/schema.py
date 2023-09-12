import strawberry

import api.schemas.category
import api.schemas.scan


@strawberry.type
class Query(api.schemas.category.Query):
    pass


@strawberry.type
class Mutation(api.schemas.category.Mutation, api.schemas.scan.Mutation):
    pass


schema = strawberry.Schema(Query, Mutation)

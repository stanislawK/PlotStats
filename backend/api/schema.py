import strawberry

import api.schemas.category


@strawberry.type
class Query(api.schemas.category.Query):
    pass


@strawberry.type
class Mutation(api.schemas.category.Mutation):
    pass


schema = strawberry.Schema(Query, Mutation)

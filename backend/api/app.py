from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from strawberry.schema import BaseSchema

from .schema import schema
from .settings import settings


def create_app() -> FastAPI:
    graphql_app: GraphQLRouter[BaseSchema, None] = GraphQLRouter(schema=schema)
    app = FastAPI(debug=settings.debug)
    app.include_router(graphql_app, prefix="/graphql")
    return app

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from .schema import schema
from .settings import settings


def create_app():
    graphql_app = GraphQLRouter(schema=schema)
    app = FastAPI(debug=settings.debug)
    app.include_router(graphql_app, prefix="/graphql")
    return app

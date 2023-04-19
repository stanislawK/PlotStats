from .schema import schema

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

def create_app():
    graphql_app = GraphQLRouter(schema=schema)
    app = FastAPI()
    app.include_router(graphql_app, prefix="/graphql")
    return app
from fastapi import FastAPI, Depends
from strawberry.fastapi import GraphQLRouter
from strawberry.schema import BaseSchema

from api.database import get_async_session
from api.schema import schema
from api.settings import settings

from sqlalchemy.ext.asyncio import AsyncSession


async def get_context(
    session: AsyncSession = Depends(get_async_session),
):
    return {
        "session": session,
    }


def create_app() -> FastAPI:
    graphql_app: GraphQLRouter[BaseSchema, None] = GraphQLRouter(
        schema=schema, context_getter=get_context
    )
    app = FastAPI(debug=settings.debug)
    app.include_router(graphql_app, prefix="/graphql")
    return app

from typing import Any

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import GraphQLRouter
from strawberry.schema import BaseSchema

from api.database import get_async_session
from api.schema import schema
from api.settings import settings
from api.utils.celery_utils import create_celery


async def get_context(
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    return {
        "session": session,
    }


def create_app() -> FastAPI:
    graphql_app: GraphQLRouter[BaseSchema, None] = GraphQLRouter(
        schema=schema, graphiql=settings.debug, context_getter=get_context  # type: ignore
    )
    app = FastAPI(debug=settings.debug)
    app.celery_app = create_celery()  # type: ignore
    app.include_router(graphql_app, prefix="/graphql")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

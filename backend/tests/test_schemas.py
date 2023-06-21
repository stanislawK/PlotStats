import pytest

from api.models import Category
from api.schema import schema

from .conftest import examples


@pytest.mark.asyncio
async def test_categories_query(client, _db_session) -> None:
    category = Category(**examples["category"])

    async with _db_session as session:
        session.add(category)
        session.commit()
    query = """
        query MyQuery {
            categories {
                name
            }
        }
    """
    result = await schema.execute(query, context_value={})
    # result = client.get("/graphql", params={"query": query})
    assert result.errors is None
    assert result.data["name"] == examples["category"]["name"]

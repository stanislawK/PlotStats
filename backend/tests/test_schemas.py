import httpx
import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from api.models import Category

from .conftest import examples


@pytest.mark.asyncio
async def test_categories_query(
    client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    category = Category(**examples["category"])
    _db_session.add(category)
    await _db_session.commit()
    query = """
        query MyQuery {
            categories {
                name
            }
        }
    """
    response = await client.get("/graphql", params={"query": query})
    assert response.status_code == 200
    result = response.json()
    assert len(result["data"]["categories"]) == 1
    assert result["data"]["categories"][0]["name"] == examples["category"]["name"]


@pytest.mark.asyncio
async def test_categories_query_fetch_id_should_fail(
    client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    category = Category(**examples["category"])
    _db_session.add(category)
    await _db_session.commit()
    query = """
        query MyQuery {
            categories {
                id
            }
        }
    """
    response = await client.get("/graphql", params={"query": query})
    assert response.status_code == 200
    result = response.json()
    assert result["data"] is None
    assert len(result["errors"]) == 1

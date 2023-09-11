import httpx
import pytest
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.models import Category
from api.types.category import CategoryExistsError

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


@pytest.mark.asyncio
async def test_create_category_mutation(
    client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    mutation = """
        mutation newCategory {
            createCategory(input: {name: "Test2"}) {
                __typename
                ... on CategoryType {
                    name
                }
                ... on CategoryExistsError {
                    message
                }
            }
        }
    """
    response = await client.post("/graphql", json={"query": mutation})
    assert response.status_code == 200
    result = response.json()
    assert result["data"]["createCategory"]["__typename"] == "CategoryType"
    assert result["data"]["createCategory"]["name"] == "Test2"
    query = select(Category).where(Category.name == "Test2")
    category_db = (await _db_session.execute(query)).scalar()
    assert category_db.name == "Test2"  # type: ignore


@pytest.mark.asyncio
async def test_create_category_mutation_duplicate_should_produce_error(
    client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    category = Category(name="Test2")
    _db_session.add(category)
    await _db_session.commit()
    mutation = """
        mutation newCategory {
            createCategory(input: {name: "Test2"}) {
                __typename
                ... on CategoryType {
                    name
                }
                ... on CategoryExistsError {
                    message
                }
            }
        }
    """
    response = await client.post("/graphql", json={"query": mutation})
    result = response.json()
    assert result["data"]["createCategory"]["__typename"] == "CategoryExistsError"
    err = CategoryExistsError()
    assert result["data"]["createCategory"]["message"] == err.message


@pytest.mark.asyncio
async def test_create_category_with_too_long_name_should_produce_error(
    client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    name = "a" * 33
    mutation = f"""
        mutation newCategory {{
            createCategory(input: {{name: "{name}"}}) {{
                __typename
                ... on CategoryType {{
                    name
                }}
                ... on CategoryExistsError {{
                    message
                }}
                ... on InputValidationError {{
                    message
                }}
            }}
        }}
    """
    response = await client.post("/graphql", json={"query": mutation})
    result = response.json()
    assert result["data"]["createCategory"]["__typename"] == "InputValidationError"
    assert (
        "ensure this value has at most 32 characters"
        in result["data"]["createCategory"]["message"]
    )


@pytest.mark.asyncio
async def test_create_category_with_too_short_name_should_produce_error(
    client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    name = ""
    mutation = f"""
        mutation newCategory {{
            createCategory(input: {{name: "{name}"}}) {{
                __typename
                ... on CategoryType {{
                    name
                }}
                ... on CategoryExistsError {{
                    message
                }}
                ... on InputValidationError {{
                    message
                }}
            }}
        }}
    """
    response = await client.post("/graphql", json={"query": mutation})
    result = response.json()
    assert result["data"]["createCategory"]["__typename"] == "InputValidationError"
    assert (
        "ensure this value has at least 1 characters "
        in result["data"]["createCategory"]["message"]
    )


@pytest.mark.asyncio
async def test_create_category_capitalize_name(
    client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    name = "test"
    mutation = f"""
        mutation newCategory {{
            createCategory(input: {{name: "{name}"}}) {{
                __typename
                ... on CategoryType {{
                    name
                }}
                ... on CategoryExistsError {{
                    message
                }}
                ... on InputValidationError {{
                    message
                }}
            }}
        }}
    """
    response = await client.post("/graphql", json={"query": mutation})
    result = response.json()
    query = select(Category)
    category_db = (await _db_session.execute(query)).scalar()
    assert result["data"]["createCategory"]["__typename"] == "CategoryType"
    assert result["data"]["createCategory"]["name"] == name.title()
    assert category_db
    assert category_db.name == name.title()


@pytest.mark.asyncio
@pytest.mark.parametrize("url", ["test", "test.com"])
async def test_adhoc_scan_invalid_input(client: httpx.AsyncClient, url: str) -> None:
    mutation = f"""
        mutation adhocScan {{
            adhocScan(input: {{url: "{url}"}}) {{
                __typename
                ... on ScanSucceeded {{
                    message
                }}
                ... on ScanFailedError {{
                    message
                }}
                ... on InputValidationError {{
                    message
                }}
            }}
        }}
    """
    response = await client.post("/graphql", json={"query": mutation})
    result = response.json()
    assert result["data"]["adhocScan"]["__typename"] == "InputValidationError"
    assert "url" in result["data"]["adhocScan"]["message"]

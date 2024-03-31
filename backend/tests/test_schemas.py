import json

import fakeredis
import httpx
import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.models import Category
from api.models.estate import Estate
from api.models.price import Price
from api.models.scan_failure import ScanFailure
from api.models.search import Search, decode_url, encode_url
from api.models.search_event import SearchEvent
from api.models.user import User
from api.types.category import CategoryExistsError
from api.utils.jwt import get_jwt_payload
from api.utils.user import get_user_by_email, verify_password

from .conftest import MockAioJSONResponse, MockAioTextResponse, examples

# mypy: ignore-errors
CATEGORIES_QUERY = """
    query categories {
        categories {
            name
        }
    }
"""

LOGIN_MUTATION: str = """
    mutation login {{
        login(input: {{
                email: "{email}", password: "{password}"
            }}) {{
            __typename
            ... on JWTPair {{
                accessToken
                refreshToken
            }}
            ... on LoginUserError {{
                __typename
                message
            }}
            ... on InputValidationError {{
                __typename
                message
            }}
        }}
    }}
"""

REFRESH_TOKEN_MUTATUON: str = """
    mutation refreshToken {
    refreshToken {
        ... on AccessToken {
        __typename
        accessToken
        }
        ... on RefreshTokenError {
        __typename
        message
        }
    }
    }
"""

REGISTER_USER_MUTATION: str = """
    mutation registerUser {{
    registerUser(input: {{email: "{email}"}}) {{
        ... on RegisterResponse {{
        __typename
        temporaryPassword
        }}
        ... on UserExistsError {{
        __typename
        message
        }}
        ... on InputValidationError {{
        __typename
        message
        }}
    }}
    }}
"""

ACTIVATE_ACCOUNT_MUTATION: str = """
mutation activateAccount {{
  activateAccount(input: {{
        email: "{email}",
        tempPassword: "{temp_password}",
        newPassword: "{new_password}"
    }}) {{
    ... on ActivateAccountSuccess {{
      __typename
      message
    }}
    ... on ActivateAccountError {{
      __typename
      message
    }}
    ... on InputValidationError {{
      __typename
      message
    }}
  }}
}}
"""

DEACTIVATE_USER_MUTATION: str = """
mutation deactivateUser {{
    deactivateUser(input: {{email: "{email}"}}) {{
        ... on DeactivateAccountSuccess {{
        __typename
        message
        }}
        ... on DeactivateAccountError {{
        __typename
        message
        }}
        ... on InputValidationError {{
        __typename
        message
        }}
    }}
    }}
"""

ALL_SEARCHES_QUERY: str = """
    query allSearches {
    allSearches {
        ... on NoSearchesAvailableError {
        __typename
        message
        }
        ... on SearchesType {
        searches {
            category {
            name
            }
            coordinates
            distanceRadius
            fromPrice
            fromSurface
            id
            location
            schedule {
            dayOfWeek
            hour
            minute
            }
            toPrice
            toSurface
            url
        }
        }
    }
    }
"""

USER_SEARCHES_QUERY: str = """
query usersSearches {
  usersSearches {
    ... on SearchesType {
      __typename
      searches {
        category {
          name
        }
        coordinates
        distanceRadius
        fromPrice
        fromSurface
        id
        location
        schedule {
          dayOfWeek
          hour
          minute
        }
        toPrice
        toSurface
        url
      }
      favoriteId
    }
    ... on NoSearchesAvailableError {
      __typename
      message
    }
  }
}
"""

ASSIGN_SEARCH_MUTATION: str = """
mutation assignSearch {{
  assignSearchToUser(input: {{id: {id}}}) {{
    ... on SearchAssignSuccessfully {{
      __typename
      message
    }}
    ... on SearchDoesntExistError {{
      __typename
      message
    }}
  }}
}}
"""

ASSIGN_FAVORITE_MUTATION: str = """
mutation assignFavoriteSearchToUser {{
  assignFavoriteSearchToUser(input: {{id: {id}}}) {{
    ... on SearchAssignSuccessfully {{
      __typename
      message
    }}
    ... on SearchDoesntExistError {{
      __typename
      message
    }}
  }}
}}
"""

FAV_SEARCH_EVENTS_STATS: str = """
query searchEventsStats {
  searchEventsStats(input: {}) {
    ... on SearchEventsStatsType {
      __typename
      searchEvents {
        avgAreaInSquareMeters
        avgPrice
        avgPricePerSquareMeter
        avgTerrainAreaInSquareMeters
        date
        minPrice {
          price
          pricePerSquareMeter
        }
        minPricePerSquareMeter {
          areaInSquareMeters
          price
          pricePerSquareMeter
        }
      }
    }
    ... on FavoriteSearchDoesntExistError {
      __typename
      message
    }
    ... on NoSearchEventError {
      __typename
      message
    }
    ... on NoPricesFoundError {
      __typename
      message
    }
  }
}
"""

SEARCH_EVENTS_STATS: str = """
query searchEventsStats {{
  searchEventsStats(input: {{id: {id}}}) {{
    ... on SearchEventsStatsType {{
      __typename
      searchEvents {{
        avgAreaInSquareMeters
        avgPrice
        avgPricePerSquareMeter
        avgTerrainAreaInSquareMeters
        date
        minPrice {{
          price
          pricePerSquareMeter
        }}
        minPricePerSquareMeter {{
          areaInSquareMeters
          price
          pricePerSquareMeter
        }}
      }}
    }}
    ... on FavoriteSearchDoesntExistError {{
      __typename
      message
    }}
    ... on NoSearchEventError {{
      __typename
      message
    }}
    ... on NoPricesFoundError {{
      __typename
      message
    }}
  }}
}}
"""

EDIT_SCHEDULE: str = """
mutation editSchedule {{
  editSchedule(input: {{
        id: {id},
        schedule: {{dayOfWeek: {day}, hour: {hour}, minute: {minute}}}
    }}) {{
    ... on ScheduleEditedSuccessfully {{
      __typename
      message
    }}
    ... on SearchDoesntExistError {{
      __typename
      message
    }}
    ... on InputValidationError {{
      __typename
      message
    }}
  }}
}}
"""

DELETE_SCHEDULE: str = """
mutation editSchedule {{
  editSchedule(input: {{id: {id}}}) {{
    ... on ScheduleEditedSuccessfully {{
      __typename
      message
    }}
    ... on SearchDoesntExistError {{
      __typename
      message
    }}
    ... on InputValidationError {{
      __typename
      message
    }}
  }}
}}
"""

USERS_LIST: str = """
query allUsers {
  allUsers {
    users {
      email
      id
      isActive
      roles
    }
  }
}
"""

LAST_STATUS_QUERY: str = """
    query searchesLastStatus {
        searchesLastStatus {
            statuses {
                id
                status
            }
        }
    }
"""


@pytest.mark.asyncio
async def test_categories_query(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    add_category: Category,
) -> None:
    response = await authenticated_client.get(
        "/graphql", params={"query": CATEGORIES_QUERY}
    )
    assert response.status_code == 200
    result = response.json()
    assert len(result["data"]["categories"]) == 1
    assert result["data"]["categories"][0]["name"] == examples["category"]["name"]


@pytest.mark.asyncio
async def test_categories_unauthenticated(
    client: httpx.AsyncClient, _db_session: AsyncSession, add_category: Category
) -> None:
    response = await client.get("/graphql", params={"query": CATEGORIES_QUERY})
    result = response.json()
    assert result["data"] is None
    assert result["errors"][0]["message"] == "User is not authenticated"


@pytest.mark.asyncio
async def test_categories_query_fetch_id_should_fail(
    client: httpx.AsyncClient, _db_session: AsyncSession, add_category: Category
) -> None:
    response = await client.get("/graphql", params={"query": CATEGORIES_QUERY})
    assert response.status_code == 200
    result = response.json()
    assert result["data"] is None
    assert len(result["errors"]) == 1


@pytest.mark.asyncio
async def test_create_category_mutation(
    admin_client: httpx.AsyncClient, _db_session: AsyncSession
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
    response = await admin_client.post("/graphql", json={"query": mutation})
    assert response.status_code == 200
    result = response.json()
    assert result["data"]["createCategory"]["__typename"] == "CategoryType"
    assert result["data"]["createCategory"]["name"] == "Test2"
    query = select(Category).where(Category.name == "Test2")
    category_db = (await _db_session.exec(query)).first()
    assert category_db.name == "Test2"  # type: ignore


@pytest.mark.asyncio
async def test_create_category_mutation_unauthorized(
    client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    mutation = """
        mutation newCategory {
            createCategory(input: {name: "Test2"}) {
                __typename
                ... on CategoryType {
                    name
                }
            }
        }
    """
    response = await client.post("/graphql", json={"query": mutation})
    assert response.status_code == 200
    result = response.json()
    assert result["data"] is None
    assert result["errors"][0]["message"] == "User is not authenticated"


@pytest.mark.asyncio
async def test_create_category_mutation_non_admin(
    authenticated_client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    mutation = """
        mutation newCategory {
            createCategory(input: {name: "Test2"}) {
                __typename
                ... on CategoryType {
                    name
                }
            }
        }
    """
    response = await authenticated_client.post("/graphql", json={"query": mutation})
    assert response.status_code == 200
    result = response.json()
    assert result["data"] is None
    assert result["errors"][0]["message"] == "User is not authenticated"


@pytest.mark.asyncio
async def test_create_category_mutation_duplicate_should_produce_error(
    admin_client: httpx.AsyncClient, _db_session: AsyncSession
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
    response = await admin_client.post("/graphql", json={"query": mutation})
    result = response.json()
    assert result["data"]["createCategory"]["__typename"] == "CategoryExistsError"
    err = CategoryExistsError()
    assert result["data"]["createCategory"]["message"] == err.message


@pytest.mark.asyncio
async def test_create_category_with_too_long_name_should_produce_error(
    admin_client: httpx.AsyncClient, _db_session: AsyncSession
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
    response = await admin_client.post("/graphql", json={"query": mutation})
    result = response.json()
    assert result["data"]["createCategory"]["__typename"] == "InputValidationError"
    assert (
        "String should have at most 32 characters"
        in result["data"]["createCategory"]["message"]
    )


@pytest.mark.asyncio
async def test_create_category_with_too_short_name_should_produce_error(
    admin_client: httpx.AsyncClient, _db_session: AsyncSession
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
    response = await admin_client.post("/graphql", json={"query": mutation})
    result = response.json()
    assert result["data"]["createCategory"]["__typename"] == "InputValidationError"
    assert (
        "String should have at least 1 character"
        in result["data"]["createCategory"]["message"]
    )


@pytest.mark.asyncio
async def test_create_category_capitalize_name(
    admin_client: httpx.AsyncClient, _db_session: AsyncSession
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
    response = await admin_client.post("/graphql", json={"query": mutation})
    result = response.json()
    query = select(Category)
    category_db = (await _db_session.exec(query)).first()
    assert result["data"]["createCategory"]["__typename"] == "CategoryType"
    assert result["data"]["createCategory"]["name"] == name.title()
    assert category_db
    assert category_db.name == name.title()


@pytest.mark.asyncio
@pytest.mark.parametrize("url", ["test", "test.com"])
async def test_adhoc_scan_invalid_input(
    authenticated_client: httpx.AsyncClient, url: str
) -> None:
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
    response = await authenticated_client.post("/graphql", json={"query": mutation})
    result = response.json()
    assert result["data"]["adhocScan"]["__typename"] == "InputValidationError"
    assert "url" in result["data"]["adhocScan"]["message"]


@pytest.mark.asyncio
@pytest.mark.parametrize("url", ["test", "test.com"])
async def test_adhoc_scan_unauthorized(client: httpx.AsyncClient, url: str) -> None:
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
    assert result["data"] is None
    assert result["errors"][0]["message"] == "User is not authenticated"


@pytest.mark.asyncio
async def test_adhoc_scan_correct_response(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    mocker: MockerFixture,
) -> None:
    category = Category(name="Plot")
    _db_session.add(category)
    await _db_session.commit()
    url = "https://www.test.io/test"
    schedule = {"day_of_week": 0, "hour": 1, "minute": 2}
    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)
    resp = MockAioJSONResponse(body, 200)
    mocker.patch("aiohttp.ClientSession.get", return_value=resp)
    schedule_mock = mocker.patch("api.parsing.setup_scan_periodic_task")
    mutation = f"""
        mutation adhocScan {{
            adhocScan(input: {{
                    url: "{url}",
                    schedule: {{hour: 1, dayOfWeek: 0, minute: 2}}
                }}) {{
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
    response = await authenticated_client.post("/graphql", json={"query": mutation})
    estates_parsed = (
        await _db_session.exec(select(Estate).options(selectinload(Estate.prices)))
    ).all()  # type: ignore
    prices_parsed = (await _db_session.exec(select(Price))).all()  # type: ignore
    search_parsed: Search = (
        await _db_session.exec(select(Search))  # type: ignore
    ).first()
    schedule_mock.assert_called_once()
    assert len(estates_parsed) == 36
    assert len(prices_parsed) == 36
    assert search_parsed.schedule == schedule
    assert len(search_parsed.users) == 1
    assert estates_parsed[0].prices[0] in prices_parsed
    assert decode_url(search_parsed.url) == url  # type: ignore
    result = response.json()
    assert result["data"]["adhocScan"]["__typename"] == "ScanSucceeded"
    assert "Scan has finished" in result["data"]["adhocScan"]["message"]


@pytest.mark.asyncio
async def test_adhoc_scan_incorrect_category(
    authenticated_client: httpx.AsyncClient, mocker: MockerFixture
) -> None:
    url = "https://www.test.io/test"
    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)
    resp = MockAioJSONResponse(body, 200)
    mocker.patch("aiohttp.ClientSession.get", return_value=resp)
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
    response = await authenticated_client.post("/graphql", json={"query": mutation})
    result = response.json()
    assert result["data"]["adhocScan"]["__typename"] == "ScanFailedError"
    assert "Document parsing failed." in result["data"]["adhocScan"]["message"]


@pytest.mark.asyncio
async def test_adhoc_scan_404_response(
    _db_session: AsyncSession,
    add_category: Category,
    authenticated_client: httpx.AsyncClient,
    mocker: MockerFixture,
    cache: fakeredis.FakeRedis,
) -> None:
    search_data = examples["search"].copy()
    url = search_data.pop("url")
    encoded_url = encode_url(url)
    search_1 = Search.model_validate(
        Search(category=add_category, url=encoded_url, **search_data)
    )
    _db_session.add(search_1)
    await _db_session.commit()
    _db_session.flush()

    with open("tests/example_files/404_resp.html", "r") as f:
        body = f.read()
    resp = MockAioTextResponse(body, 404)
    mocker.patch("aiohttp.ClientSession.get", return_value=resp)
    mocker.patch("asyncio.sleep", return_value=0)
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
    response = await authenticated_client.post("/graphql", json={"query": mutation})
    result = response.json()
    assert result["data"]["adhocScan"]["__typename"] == "ScanFailedError"
    assert (
        "Scan has failed with 404 status code."
        in result["data"]["adhocScan"]["message"]
    )
    assert cache.get("token") == "U-X80D14b5VUVY_qgIbBQ"
    failure_db = (await _db_session.exec(select(ScanFailure))).first()
    assert failure_db.search_id == search_1.id
    assert failure_db.status_code == 404


@pytest.mark.asyncio
async def test_search_event_stats_without_top(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    mocker: MockerFixture,
) -> None:
    """
    SETUP
    """
    category = Category(name="Plot")
    _db_session.add(category)
    await _db_session.commit()
    url = "https://www.test.io/test"
    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)
    resp = MockAioJSONResponse(body, 200)
    mocker.patch("aiohttp.ClientSession.get", return_value=resp)
    mutation = f"""
        mutation adhocScan {{
            adhocScan(input: {{
                    url: "{url}"
                }}) {{
                __typename
                ... on ScanSucceeded {{
                    message
                }}
            }}
        }}
    """
    await authenticated_client.post("/graphql", json={"query": mutation})
    search_event = (await _db_session.exec(select(SearchEvent))).first()
    query = f"""
        query eventStats {{
            searchEventStats(input: {{
                    id: {search_event.id}
                }}) {{
                __typename
                ... on EventStatsType {{
                avgAreaInSquareMeters
                avgTerrainAreaInSquareMeters
                avgPrice
                avgPricePerSquareMeter
                minPrice {{
                    price
                    areaInSquareMeters
                    estate {{
                    title
                    }}
                }}
                minPricePerSquareMeter {{
                    areaInSquareMeters
                    price
                    pricePerSquareMeter
                    estate {{
                    title
                    }}
                }}
                }}
                ... on SearchEventDoesntExistError {{
                    message
                }}
                ... on NoPricesFoundError {{
                    message
                }}
            }}
        }}
    """
    response = await authenticated_client.post("/graphql", json={"query": query})
    result = response.json()["data"]["searchEventStats"]
    expected_result = {
        "__typename": "EventStatsType",
        "avgAreaInSquareMeters": 1075.25,
        "avgPrice": 132315.72,
        "avgPricePerSquareMeter": 158.67,
        "avgTerrainAreaInSquareMeters": None,
        "minPrice": {
            "areaInSquareMeters": 1242,
            "estate": {"title": '"Działki na Żuławach"'},
            "price": 100000,
        },
        "minPricePerSquareMeter": {
            "areaInSquareMeters": 4900,
            "estate": {"title": "Z warunkami zabudowy nad " "Wisłą, piękna sceneria!"},
            "price": 129000,
            "pricePerSquareMeter": 26,
        },
    }
    assert result == expected_result


@pytest.mark.asyncio
async def test_search_event_doesnt_exist(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    mocker: MockerFixture,
) -> None:
    """
    SETUP
    """
    category = Category(name="Plot")
    _db_session.add(category)
    await _db_session.commit()
    url = "https://www.test.io/test"
    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)
    resp = MockAioJSONResponse(body, 200)
    mocker.patch("aiohttp.ClientSession.get", return_value=resp)
    mutation = f"""
        mutation adhocScan {{
            adhocScan(input: {{
                    url: "{url}"
                }}) {{
                __typename
                ... on ScanSucceeded {{
                    message
                }}
            }}
        }}
    """
    await authenticated_client.post("/graphql", json={"query": mutation})
    search_event = (await _db_session.exec(select(SearchEvent))).first()
    query = f"""
        query eventStats {{
            searchEventStats(input: {{
                    id: {search_event.id + 1}
                }}) {{
                __typename
                ... on EventStatsType {{
                    avgPrice
                }}
                ... on SearchEventDoesntExistError {{
                    message
                }}
                ... on NoPricesFoundError {{
                    message
                }}
            }}
        }}
    """
    response = await authenticated_client.post("/graphql", json={"query": query})
    result = response.json()["data"]["searchEventStats"]
    assert result["__typename"] == "SearchEventDoesntExistError"
    assert result["message"] == "Search Event with provided id doesn't exist"


@pytest.mark.asyncio
async def test_search_event_unauthorized(
    authenticated_client: httpx.AsyncClient,
    client: httpx.AsyncClient,
    _db_session: AsyncSession,
    mocker: MockerFixture,
) -> None:
    """
    SETUP
    """
    category = Category(name="Plot")
    _db_session.add(category)
    await _db_session.commit()
    url = "https://www.test.io/test"
    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)
    resp = MockAioJSONResponse(body, 200)
    mocker.patch("aiohttp.ClientSession.get", return_value=resp)
    mutation = f"""
        mutation adhocScan {{
            adhocScan(input: {{
                    url: "{url}"
                }}) {{
                __typename
                ... on ScanSucceeded {{
                    message
                }}
            }}
        }}
    """
    await authenticated_client.post("/graphql", json={"query": mutation})
    search_event = (await _db_session.exec(select(SearchEvent))).first()
    query = f"""
        query eventStats {{
            searchEventStats(input: {{
                    id: {search_event.id + 1}
                }}) {{
                __typename
                ... on EventStatsType {{
                    avgPrice
                }}
                ... on SearchEventDoesntExistError {{
                    message
                }}
                ... on NoPricesFoundError {{
                    message
                }}
            }}
        }}
    """
    response = await client.post("/graphql", json={"query": query})
    result = response.json()
    assert result["data"] is None
    assert result["errors"][0]["message"] == "User is not authenticated"


@pytest.mark.asyncio
async def test_search_doesnt_exist(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    mocker: MockerFixture,
) -> None:
    """
    SETUP
    """
    category = Category(name="Plot")
    _db_session.add(category)
    await _db_session.commit()
    url = "https://www.test.io/test"
    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)
    resp = MockAioJSONResponse(body, 200)
    mocker.patch("aiohttp.ClientSession.get", return_value=resp)
    mutation = f"""
        mutation adhocScan {{
            adhocScan(input: {{
                    url: "{url}"
                }}) {{
                __typename
                ... on ScanSucceeded {{
                    message
                }}
            }}
        }}
    """
    await authenticated_client.post("/graphql", json={"query": mutation})
    search = (await _db_session.exec(select(Search))).first()
    query = f"""
        query searchStats {{
            searchStats(input: {{
                    id: {search.id + 1}
                }}) {{
                __typename
                ... on SearchStatsType {{
                    avgPriceTotal
                }}
                ... on SearchDoesntExistError {{
                    message
                }}
            }}
        }}
    """
    response = await authenticated_client.post("/graphql", json={"query": query})
    result = response.json()["data"]["searchStats"]
    assert result["__typename"] == "SearchDoesntExistError"
    assert result["message"] == "Search with provided id doesn't exist"


@pytest.mark.asyncio
async def test_search_stats_query(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    mocker: MockerFixture,
) -> None:
    """
    SETUP
    """
    category = Category(name="Plot")
    _db_session.add(category)
    await _db_session.commit()
    url = "https://www.test.io/test"
    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)
    resp = MockAioJSONResponse(body, 200)
    mocker.patch("aiohttp.ClientSession.get", return_value=resp)
    mutation = f"""
        mutation adhocScan {{
            adhocScan(input: {{
                    url: "{url}"
                }}) {{
                __typename
                ... on ScanSucceeded {{
                    message
                }}
            }}
        }}
    """
    await authenticated_client.post("/graphql", json={"query": mutation})
    await authenticated_client.post("/graphql", json={"query": mutation})
    search = (await _db_session.exec(select(Search))).first()
    assert len(search.users) == 1
    query = f"""
        query searchStats {{
            searchStats(input: {{
                    id: {search.id}
                }}) {{
                __typename
                ... on SearchStatsType {{
                    avgAreaTotal
                    avgTerrainTotal
                    avgPricePerSquareMeterTotal
                    avgPriceTotal
                    category {{
                        name
                    }}
                    dateFrom
                    dateTo
                    distanceRadius
                    events {{
                        avgAreaInSquareMeters
                        avgPrice
                        avgPricePerSquareMeter
                        avgTerrainAreaInSquareMeters
                    }}
                    location
                    fromPrice
                    toPrice
                }}
                ... on SearchDoesntExistError {{
                    message
                }}
            }}
        }}
    """
    response = await authenticated_client.post("/graphql", json={"query": query})
    result = response.json()["data"]["searchStats"]
    expected = {
        "__typename": "SearchStatsType",
        "avgAreaTotal": 1075.25,
        "avgPricePerSquareMeterTotal": 158.67,
        "avgPriceTotal": 132315.72,
        "avgTerrainTotal": None,
        "category": {"name": "Plot"},
        "distanceRadius": 15,
        "events": [
            {
                "avgAreaInSquareMeters": 1075.25,
                "avgPrice": 132315.72,
                "avgPricePerSquareMeter": 158.67,
                "avgTerrainAreaInSquareMeters": None,
            },
            {
                "avgAreaInSquareMeters": 1075.25,
                "avgPrice": 132315.72,
                "avgPricePerSquareMeter": 158.67,
                "avgTerrainAreaInSquareMeters": None,
            },
        ],
        "fromPrice": 100000,
        "location": "Gdańsk, pomorskie",
        "toPrice": 150000,
    }
    result.pop("dateFrom")
    result.pop("dateTo")
    assert result == expected


@pytest.mark.asyncio
async def test_search_stats_query_unauthorized(
    client: httpx.AsyncClient,
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    mocker: MockerFixture,
) -> None:
    """
    SETUP
    """
    category = Category(name="Plot")
    _db_session.add(category)
    await _db_session.commit()
    url = "https://www.test.io/test"
    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)
    resp = MockAioJSONResponse(body, 200)
    mocker.patch("aiohttp.ClientSession.get", return_value=resp)
    mutation = f"""
        mutation adhocScan {{
            adhocScan(input: {{
                    url: "{url}"
                }}) {{
                __typename
                ... on ScanSucceeded {{
                    message
                }}
            }}
        }}
    """
    await authenticated_client.post("/graphql", json={"query": mutation})
    await authenticated_client.post("/graphql", json={"query": mutation})
    search = (await _db_session.exec(select(Search))).first()
    query = f"""
        query searchStats {{
            searchStats(input: {{
                    id: {search.id}
                }}) {{
                __typename
                ... on SearchStatsType {{
                    avgAreaTotal
                }}
                ... on SearchDoesntExistError {{
                    message
                }}
            }}
        }}
    """
    response = await client.post("/graphql", json={"query": query})
    result = response.json()
    assert result["data"] is None
    assert result["errors"][0]["message"] == "User is not authenticated"


@pytest.mark.asyncio
async def test_login_correct_credentials(
    client: httpx.AsyncClient, _db_session: AsyncSession, add_user: User
) -> None:
    """
    SETUP
    """
    email, password = examples["user"]["email"], examples["user"]["password"]
    response = await client.post(
        "/graphql",
        json={"query": LOGIN_MUTATION.format(email=email, password=password)},
    )
    result = response.json()["data"]["login"]
    assert result["__typename"] == "JWTPair"
    access_token, refresh_token = result["accessToken"], result["refreshToken"]
    access_token_decoded, refresh_token_decoded = get_jwt_payload(
        access_token
    ), get_jwt_payload(refresh_token)
    assert access_token_decoded["sub"] == str(add_user.id)
    assert refresh_token_decoded["sub"] == str(add_user.id)
    assert access_token_decoded["fresh"] is True
    assert refresh_token_decoded["fresh"] is False
    assert access_token_decoded["type"] == "access"
    assert refresh_token_decoded["type"] == "refresh"


@pytest.mark.asyncio
async def test_login_wrong_credentials(
    client: httpx.AsyncClient, _db_session: AsyncSession, add_user: User
) -> None:
    """
    SETUP
    """
    email, password = "invalid_email", examples["user"]["password"]
    response = await client.post(
        "/graphql",
        json={"query": LOGIN_MUTATION.format(email=email, password=password)},
    )
    result = response.json()["data"]["login"]
    assert result["__typename"] == "LoginUserError"
    assert result["message"] == "Login user error"

    email, password = examples["user"]["email"], "invalid_password"
    response = await client.post(
        "/graphql",
        json={"query": LOGIN_MUTATION.format(email=email, password=password)},
    )
    result = response.json()["data"]["login"]
    assert result["__typename"] == "LoginUserError"
    assert result["message"] == "Login user error"


@pytest.mark.asyncio
async def test_access_resource_with_refresh_token_should_fail(
    client: httpx.AsyncClient,
    _db_session: AsyncSession,
    add_user: User,
    add_category: Category,
) -> None:
    email, password = examples["user"]["email"], examples["user"]["password"]
    response = await client.post(
        "/graphql",
        json={"query": LOGIN_MUTATION.format(email=email, password=password)},
    )
    result = response.json()["data"]["login"]
    assert result["__typename"] == "JWTPair"
    access_token, refresh_token = result["accessToken"], result["refreshToken"]

    response = await client.get(
        "/graphql",
        params={"query": CATEGORIES_QUERY},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    result = response.json()
    assert len(result["data"]["categories"]) == 1

    response = await client.get(
        "/graphql",
        params={"query": CATEGORIES_QUERY},
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    result = response.json()
    assert result["data"] is None
    assert result["errors"][0]["message"] == "User is not authenticated"


@pytest.mark.asyncio
async def test_access_resource_with_stale_access_token(
    client: httpx.AsyncClient,
    _db_session: AsyncSession,
    add_user: User,
    add_category: Category,
) -> None:
    with freeze_time("2022-01-01 00:00:00") as frozen_time:
        email, password = examples["user"]["email"], examples["user"]["password"]
        response = await client.post(
            "/graphql",
            json={"query": LOGIN_MUTATION.format(email=email, password=password)},
        )
        result = response.json()["data"]["login"]
        assert result["__typename"] == "JWTPair"
        access_token, _ = result["accessToken"], result["refreshToken"]

        frozen_time.move_to("2022-01-01 00:31:00")
        response = await client.get(
            "/graphql",
            params={"query": CATEGORIES_QUERY},
            headers={"Authorization": f"Bearer {access_token}"},
        )
    result = response.json()
    assert result["data"] is None
    assert result["errors"][0]["message"] == "User is not authenticated"


@pytest.mark.asyncio
async def test_refresh_access_token_correct(
    client: httpx.AsyncClient,
    _db_session: AsyncSession,
    add_user: User,
    add_category: Category,
) -> None:
    with freeze_time("2022-01-01 00:00:00") as frozen_time:
        email, password = examples["user"]["email"], examples["user"]["password"]
        login_response = await client.post(
            "/graphql",
            json={"query": LOGIN_MUTATION.format(email=email, password=password)},
        )
        login_result = login_response.json()["data"]["login"]
        access_token, refresh_token = (
            login_result["accessToken"],
            login_result["refreshToken"],
        )
        frozen_time.move_to("2022-01-01 00:31:00")
        response = await client.post(
            "/graphql",
            json={"query": REFRESH_TOKEN_MUTATUON},
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        refresh_result = response.json()["data"]["refreshToken"]
        new_token = refresh_result["accessToken"]
        assert new_token != access_token
        token_payload = get_jwt_payload(new_token)
        assert token_payload["fresh"] is False
        assert token_payload["type"] == "access"
        categories_response = await client.get(
            "/graphql",
            params={"query": CATEGORIES_QUERY},
            headers={"Authorization": f"Bearer {new_token}"},
        )
        categories_result = categories_response.json()
        assert len(categories_result["data"]["categories"]) == 1


@pytest.mark.asyncio
async def test_refresh_access_token_with_access_token_should_fail(
    client: httpx.AsyncClient,
    _db_session: AsyncSession,
    add_user: User,
    add_category: Category,
) -> None:
    email, password = examples["user"]["email"], examples["user"]["password"]
    login_response = await client.post(
        "/graphql",
        json={"query": LOGIN_MUTATION.format(email=email, password=password)},
    )
    login_result = login_response.json()["data"]["login"]
    access_token, _ = (
        login_result["accessToken"],
        login_result["refreshToken"],
    )

    response = await client.post(
        "/graphql",
        json={"query": REFRESH_TOKEN_MUTATUON},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    result = response.json()
    assert result["data"] is None
    assert result["errors"][0]["message"] == "User is not authenticated"


@pytest.mark.asyncio
async def test_refresh_access_token_without_token_should_fail(
    client: httpx.AsyncClient,
    _db_session: AsyncSession,
    add_user: User,
    add_category: Category,
) -> None:
    response = await client.post("/graphql", json={"query": REFRESH_TOKEN_MUTATUON})
    result = response.json()
    assert result["data"] is None
    assert result["errors"][0]["message"] == "User is not authenticated"


@pytest.mark.asyncio
async def test_refresh_access_token_stale_refresh_token(
    client: httpx.AsyncClient,
    _db_session: AsyncSession,
    add_user: User,
    add_category: Category,
) -> None:
    with freeze_time("2022-01-01 00:00:00") as frozen_time:
        email, password = examples["user"]["email"], examples["user"]["password"]
        login_response = await client.post(
            "/graphql",
            json={"query": LOGIN_MUTATION.format(email=email, password=password)},
        )
        login_result = login_response.json()["data"]["login"]
        _, refresh_token = (
            login_result["accessToken"],
            login_result["refreshToken"],
        )
        frozen_time.move_to("2022-01-03 00:31:00")
        response = await client.post(
            "/graphql",
            json={"query": REFRESH_TOKEN_MUTATUON},
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        result = response.json()
        assert result["data"] is None
        assert result["errors"][0]["message"] == "User is not authenticated"


@pytest.mark.asyncio
async def test_create_user_mutation(
    admin_client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    email = "new_user@test.com"
    response = await admin_client.post(
        "/graphql", json={"query": REGISTER_USER_MUTATION.format(email=email)}
    )
    assert response.status_code == 200
    result = response.json()
    assert result["data"]["registerUser"]["__typename"] == "RegisterResponse"
    temp_pass = result["data"]["registerUser"]["temporaryPassword"]
    assert len(temp_pass) > 1
    new_user = await get_user_by_email(email=email, session=_db_session)
    assert new_user is not None
    assert new_user.is_active is False
    assert verify_password(temp_pass, new_user.password)


@pytest.mark.asyncio
async def test_create_user_mutation_non_admin_should_fail(
    authenticated_client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    email = "new_user@test.com"
    response = await authenticated_client.post(
        "/graphql", json={"query": REGISTER_USER_MUTATION.format(email=email)}
    )
    result = response.json()
    assert result["data"] is None
    assert result["errors"][0]["message"] == "User is not authenticated"


@pytest.mark.asyncio
async def test_create_user_mutation_without_fresh_token(
    admin_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    add_admin: User,
    add_category: Category,
) -> None:
    email, password = examples["user"]["email"], examples["user"]["password"]
    login_response = await admin_client.post(
        "/graphql",
        json={"query": LOGIN_MUTATION.format(email=email, password=password)},
    )
    login_result = login_response.json()["data"]["login"]
    _, refresh_token = (
        login_result["accessToken"],
        login_result["refreshToken"],
    )
    response = await admin_client.post(
        "/graphql",
        json={"query": REFRESH_TOKEN_MUTATUON},
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    refresh_result = response.json()["data"]["refreshToken"]
    new_token = refresh_result["accessToken"]
    new_user_email = "new_user@test.com"
    response = await admin_client.post(
        "/graphql",
        headers={"Authorization": f"Bearer {new_token}"},
        json={"query": REGISTER_USER_MUTATION.format(email=new_user_email)},
    )
    result = response.json()
    assert result["data"] is None
    assert result["errors"][0]["message"] == "Please login again"


@pytest.mark.asyncio
async def test_create_user_mutation_invalid_email(
    admin_client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    email = "new_user_test.com"
    response = await admin_client.post(
        "/graphql", json={"query": REGISTER_USER_MUTATION.format(email=email)}
    )
    result = response.json()
    assert result["data"]["registerUser"]["__typename"] == "InputValidationError"
    assert "validation error for UserEmail" in result["data"]["registerUser"]["message"]


@pytest.mark.asyncio
async def test_create_user_twice_mutation(
    admin_client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    email = "new_user@test.com"
    await admin_client.post(
        "/graphql", json={"query": REGISTER_USER_MUTATION.format(email=email)}
    )
    response = await admin_client.post(
        "/graphql", json={"query": REGISTER_USER_MUTATION.format(email=email)}
    )
    result = response.json()
    assert result["data"]["registerUser"]["__typename"] == "UserExistsError"
    assert (
        "User with that email already exists"
        in result["data"]["registerUser"]["message"]
    )


@pytest.mark.asyncio
async def test_activate_account_mutation(
    admin_client: httpx.AsyncClient,
    client: httpx.AsyncClient,
    _db_session: AsyncSession,
) -> None:
    email = "new_user@test.com"
    response = await admin_client.post(
        "/graphql", json={"query": REGISTER_USER_MUTATION.format(email=email)}
    )
    result = response.json()
    temp_pass = result["data"]["registerUser"]["temporaryPassword"]
    new_pass = "1BrandNewP@ssword"
    activate_response = await admin_client.post(
        "/graphql",
        json={
            "query": ACTIVATE_ACCOUNT_MUTATION.format(
                email=email, temp_password=temp_pass, new_password=new_pass
            )
        },
    )
    activate_result = activate_response.json()
    assert (
        activate_result["data"]["activateAccount"]["__typename"]
        == "ActivateAccountSuccess"
    )
    assert (
        activate_result["data"]["activateAccount"]["message"]
        == "Activated account successfully"
    )
    activated_user = await get_user_by_email(email=email, session=_db_session)
    assert activated_user is not None
    assert activated_user.is_active is True
    assert not verify_password(temp_pass, activated_user.password)
    assert verify_password(new_pass, activated_user.password)


@pytest.mark.asyncio
async def test_activate_account_invalid_input(
    admin_client: httpx.AsyncClient,
    client: httpx.AsyncClient,
    _db_session: AsyncSession,
) -> None:
    email = "new_user@test.com"
    response = await admin_client.post(
        "/graphql", json={"query": REGISTER_USER_MUTATION.format(email=email)}
    )
    result = response.json()
    temp_pass = result["data"]["registerUser"]["temporaryPassword"]
    new_pass_weak = "newpassword"
    activate_response = await admin_client.post(
        "/graphql",
        json={
            "query": ACTIVATE_ACCOUNT_MUTATION.format(
                email=email, temp_password=temp_pass, new_password=new_pass_weak
            )
        },
    )
    activate_result = activate_response.json()
    weak_psd_msg = (
        "Password must contain at least one uppercase letter, "
        "one lowercase letter, one digit, and one special character"
    )
    assert (
        activate_result["data"]["activateAccount"]["__typename"]
        == "InputValidationError"
    )
    assert weak_psd_msg in activate_result["data"]["activateAccount"]["message"]

    activate_response = await admin_client.post(
        "/graphql",
        json={
            "query": ACTIVATE_ACCOUNT_MUTATION.format(
                email=email, temp_password=temp_pass, new_password=temp_pass
            )
        },
    )
    activate_result = activate_response.json()
    assert (
        activate_result["data"]["activateAccount"]["__typename"]
        == "InputValidationError"
    )
    assert (
        weak_psd_msg in activate_result["data"]["activateAccount"]["message"]
        or "New password cannot be the same as temporary password"
        in activate_result["data"]["activateAccount"]["message"]
    )
    new_user = await get_user_by_email(email=email, session=_db_session)
    assert new_user is not None
    assert new_user.is_active is False
    assert verify_password(temp_pass, new_user.password)
    assert not verify_password(new_pass_weak, new_user.password)


@pytest.mark.asyncio
async def test_activate_account_user_already_active(
    admin_client: httpx.AsyncClient,
    client: httpx.AsyncClient,
    _db_session: AsyncSession,
) -> None:
    email = "new_user@test.com"
    response = await admin_client.post(
        "/graphql", json={"query": REGISTER_USER_MUTATION.format(email=email)}
    )
    result = response.json()
    temp_pass = result["data"]["registerUser"]["temporaryPassword"]
    new_pass = "1BrandNewP@ssword"
    new_user = await get_user_by_email(email=email, session=_db_session)
    new_user.is_active = True
    _db_session.add(new_user)
    await _db_session.commit()
    activate_response = await admin_client.post(
        "/graphql",
        json={
            "query": ACTIVATE_ACCOUNT_MUTATION.format(
                email=email, temp_password=temp_pass, new_password=new_pass
            )
        },
    )
    activate_result = activate_response.json()
    assert (
        activate_result["data"]["activateAccount"]["__typename"]
        == "ActivateAccountError"
    )
    assert "Activation error" in activate_result["data"]["activateAccount"]["message"]


@pytest.mark.asyncio
async def test_activate_account_deactivated_should_fail(
    admin_client: httpx.AsyncClient,
    client: httpx.AsyncClient,
    _db_session: AsyncSession,
) -> None:
    email = "new_user@test.com"
    response = await admin_client.post(
        "/graphql", json={"query": REGISTER_USER_MUTATION.format(email=email)}
    )
    result = response.json()
    temp_pass = result["data"]["registerUser"]["temporaryPassword"]
    new_pass = "1BrandNewP@ssword"
    new_user = await get_user_by_email(email=email, session=_db_session)
    new_user.roles = ["deactivated"]
    _db_session.add(new_user)
    await _db_session.commit()
    activate_response = await admin_client.post(
        "/graphql",
        json={
            "query": ACTIVATE_ACCOUNT_MUTATION.format(
                email=email, temp_password=temp_pass, new_password=new_pass
            )
        },
    )
    activate_result = activate_response.json()
    assert (
        activate_result["data"]["activateAccount"]["__typename"]
        == "ActivateAccountError"
    )
    assert "Activation error" in activate_result["data"]["activateAccount"]["message"]


@pytest.mark.asyncio
async def test_deactivate_user_mutation(
    admin_client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    email = "new_user@test.com"
    await admin_client.post(
        "/graphql", json={"query": REGISTER_USER_MUTATION.format(email=email)}
    )
    new_user = await get_user_by_email(email=email, session=_db_session)
    new_user.is_active = True
    _db_session.add(new_user)
    await _db_session.commit()
    response = await admin_client.post(
        "/graphql", json={"query": DEACTIVATE_USER_MUTATION.format(email=email)}
    )
    result = response.json()
    assert result["data"]["deactivateUser"]["__typename"] == "DeactivateAccountSuccess"
    assert (
        result["data"]["deactivateUser"]["message"]
        == "Deactivated account successfully"
    )
    deactivated_user = await get_user_by_email(email=email, session=_db_session)
    assert deactivated_user.is_active is False
    assert deactivated_user.roles == ["deactivated"]


@pytest.mark.asyncio
async def test_deactivate_user_mutation_user_does_not_exist(
    admin_client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    email = "new_user@test.com"
    response = await admin_client.post(
        "/graphql", json={"query": DEACTIVATE_USER_MUTATION.format(email=email)}
    )
    result = response.json()
    assert result["data"]["deactivateUser"]["__typename"] == "DeactivateAccountError"
    assert result["data"]["deactivateUser"]["message"] == "Deactivation error"


@pytest.mark.asyncio
async def test_searches_query_no_searches_error(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
) -> None:
    response = await authenticated_client.get(
        "/graphql", params={"query": ALL_SEARCHES_QUERY}
    )
    result = response.json()
    assert result["data"]["allSearches"]["__typename"] == "NoSearchesAvailableError"
    assert result["data"]["allSearches"]["message"] == "No searches available"


@pytest.mark.asyncio
async def test_searches_query(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    add_category: Category,
) -> None:
    search = Search(**examples["search"])
    search.category = add_category
    search.url = encode_url(examples["search"]["url"])
    _db_session.add(search)
    await _db_session.commit()
    response = await authenticated_client.get(
        "/graphql", params={"query": ALL_SEARCHES_QUERY}
    )
    result = response.json()
    searches = result["data"]["allSearches"]["searches"]
    assert len(searches) == 1
    search_res = searches[0]
    assert search_res["id"] == search.id
    assert search_res["category"]["name"] == add_category.name
    assert search_res["distanceRadius"] == search.distance_radius
    assert search_res["fromPrice"] == search.from_price
    assert search_res["toPrice"] == search.to_price
    assert search_res["location"] == search.location
    assert search_res["fromSurface"] == search.from_surface
    assert search_res["toSurface"] == search.to_surface
    assert search_res["schedule"] is None
    assert search_res["url"] == decode_url(search.url)


@pytest.mark.asyncio
async def test_user_searches_query_no_searches(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    add_category: Category,
) -> None:
    search = Search(**examples["search"])
    search.category = add_category
    _db_session.add(search)
    await _db_session.commit()
    response = await authenticated_client.get(
        "/graphql", params={"query": USER_SEARCHES_QUERY}
    )
    result = response.json()
    assert result["data"]["usersSearches"]["__typename"] == "NoSearchesAvailableError"
    assert result["data"]["usersSearches"]["message"] == "No searches available"


@pytest.mark.asyncio
async def test_user_searches_query(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    add_category: Category,
    add_user: User,
) -> None:
    search = Search(**examples["search"])
    users_search = Search(
        users=[add_user],
        category=add_category,
        **{**examples["search"], "url": encode_url("https://www.test.io/test2")},
    )
    search.category = add_category
    search.url = encode_url(examples["search"]["url"])
    _db_session.add(search)
    _db_session.add(users_search)
    await _db_session.flush()
    add_user.favorite_search_id = search.id
    _db_session.add(add_user)
    await _db_session.commit()
    response = await authenticated_client.get(
        "/graphql", params={"query": USER_SEARCHES_QUERY}
    )
    result = response.json()
    assert result["data"]["usersSearches"]["__typename"] == "SearchesType"
    searches = result["data"]["usersSearches"]["searches"]
    assert len(searches) == 1
    search_res = searches[0]
    assert search_res["id"] != search.id
    assert search_res["id"] == users_search.id
    assert search_res["category"]["name"] == add_category.name
    assert search_res["distanceRadius"] == users_search.distance_radius
    assert search_res["fromPrice"] == users_search.from_price
    assert search_res["toPrice"] == users_search.to_price
    assert search_res["location"] == users_search.location
    assert search_res["fromSurface"] == users_search.from_surface
    assert search_res["toSurface"] == users_search.to_surface
    assert search_res["schedule"] is None
    assert search_res["url"] == decode_url(users_search.url)
    assert result["data"]["usersSearches"]["favoriteId"] == search.id


@pytest.mark.asyncio
async def test_assign_search_to_user(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    add_category: Category,
    add_user: User,
) -> None:
    search = Search(**examples["search"])
    search.category = add_category
    _db_session.add(search)
    await _db_session.commit()
    response = await authenticated_client.post(
        "/graphql", json={"query": ASSIGN_SEARCH_MUTATION.format(id=search.id)}
    )
    result = response.json()
    search = (await _db_session.exec(select(Search))).first()
    assert (
        result["data"]["assignSearchToUser"]["__typename"] == "SearchAssignSuccessfully"
    )
    assert (
        result["data"]["assignSearchToUser"]["message"]
        == "Search assigned successfully"
    )
    assert search.users[0].id == add_user.id


@pytest.mark.asyncio
async def test_assign_search_to_user_twice(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    add_category: Category,
    add_user: User,
) -> None:
    search = Search(**examples["search"])
    search.category = add_category
    search.users.append(add_user)
    _db_session.add(search)
    await _db_session.commit()
    response = await authenticated_client.post(
        "/graphql", json={"query": ASSIGN_SEARCH_MUTATION.format(id=search.id)}
    )
    result = response.json()
    search = (await _db_session.exec(select(Search))).first()
    assert (
        result["data"]["assignSearchToUser"]["__typename"] == "SearchAssignSuccessfully"
    )
    assert search.users[0].id == add_user.id
    assert len(search.users) == 1


@pytest.mark.asyncio
async def test_assign_search_doesnt_exist(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    add_category: Category,
    add_user: User,
) -> None:
    search = Search(**examples["search"])
    search.category = add_category
    _db_session.add(search)
    await _db_session.commit()
    response = await authenticated_client.post(
        "/graphql", json={"query": ASSIGN_SEARCH_MUTATION.format(id=search.id + 1)}
    )
    result = response.json()
    assert (
        result["data"]["assignSearchToUser"]["__typename"] == "SearchDoesntExistError"
    )
    assert (
        result["data"]["assignSearchToUser"]["message"]
        == "Search with provided id doesn't exist"
    )


@pytest.mark.asyncio
async def test_assign_favorite_search_to_user(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    add_category: Category,
    add_user: User,
) -> None:
    search = Search(**examples["search"])
    search.category = add_category
    _db_session.add(search)
    await _db_session.commit()
    response = await authenticated_client.post(
        "/graphql", json={"query": ASSIGN_FAVORITE_MUTATION.format(id=search.id)}
    )
    result = response.json()
    user = (await _db_session.exec(select(User))).first()
    assert (
        result["data"]["assignFavoriteSearchToUser"]["__typename"]
        == "SearchAssignSuccessfully"
    )
    assert (
        result["data"]["assignFavoriteSearchToUser"]["message"]
        == "Search assigned successfully"
    )
    assert user.favorite_search_id == search.id


@pytest.mark.asyncio
async def test_assign_favorite_search_doesnt_exist(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    add_category: Category,
    add_user: User,
) -> None:
    search = Search(**examples["search"])
    search.category = add_category
    _db_session.add(search)
    await _db_session.commit()
    response = await authenticated_client.post(
        "/graphql", json={"query": ASSIGN_FAVORITE_MUTATION.format(id=search.id + 1)}
    )
    result = response.json()
    assert (
        result["data"]["assignFavoriteSearchToUser"]["__typename"]
        == "SearchDoesntExistError"
    )
    assert (
        result["data"]["assignFavoriteSearchToUser"]["message"]
        == "Search with provided id doesn't exist"
    )


@pytest.mark.asyncio
async def test_fav_search_event_stats(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    mocker: MockerFixture,
) -> None:
    category = Category(name="Plot")
    _db_session.add(category)
    await _db_session.commit()
    url = "https://www.test.io/test"
    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)
    resp = MockAioJSONResponse(body, 200)
    mocker.patch("aiohttp.ClientSession.get", return_value=resp)
    mutation = f"""
        mutation adhocScan {{
            adhocScan(input: {{
                    url: "{url}"
                }}) {{
                __typename
                ... on ScanSucceeded {{
                    message
                }}
            }}
        }}
    """
    await authenticated_client.post("/graphql", json={"query": mutation})
    search = (await _db_session.exec(select(Search))).first()
    await authenticated_client.post(
        "/graphql", json={"query": ASSIGN_FAVORITE_MUTATION.format(id=search.id)}
    )

    response = await authenticated_client.post(
        "/graphql", json={"query": FAV_SEARCH_EVENTS_STATS}
    )
    result = response.json()["data"]["searchEventsStats"]
    expected_result = {
        "__typename": "SearchEventsStatsType",
        "searchEvents": [
            {
                "avgAreaInSquareMeters": 1075.25,
                "avgPrice": 132315.72,
                "avgPricePerSquareMeter": 158.67,
                "avgTerrainAreaInSquareMeters": None,
                "minPrice": {
                    "pricePerSquareMeter": 81,
                    "price": 100000,
                },
                "minPricePerSquareMeter": {
                    "areaInSquareMeters": 4900,
                    "price": 129000,
                    "pricePerSquareMeter": 26,
                },
            }
        ],
    }
    date = result["searchEvents"][0].pop("date")
    assert date is not None
    assert result == expected_result


@pytest.mark.asyncio
async def test_search_events_stats(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    mocker: MockerFixture,
) -> None:
    category = Category(name="Plot")
    _db_session.add(category)
    await _db_session.commit()
    url = "https://www.test.io/test"
    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)
    resp = MockAioJSONResponse(body, 200)
    mocker.patch("aiohttp.ClientSession.get", return_value=resp)
    mutation = f"""
        mutation adhocScan {{
            adhocScan(input: {{
                    url: "{url}"
                }}) {{
                __typename
                ... on ScanSucceeded {{
                    message
                }}
            }}
        }}
    """
    await authenticated_client.post("/graphql", json={"query": mutation})
    search = (await _db_session.exec(select(Search))).first()

    response = await authenticated_client.post(
        "/graphql", json={"query": SEARCH_EVENTS_STATS.format(id=search.id)}
    )
    result = response.json()["data"]["searchEventsStats"]
    expected_result = {
        "__typename": "SearchEventsStatsType",
        "searchEvents": [
            {
                "avgAreaInSquareMeters": 1075.25,
                "avgPrice": 132315.72,
                "avgPricePerSquareMeter": 158.67,
                "avgTerrainAreaInSquareMeters": None,
                "minPrice": {
                    "pricePerSquareMeter": 81,
                    "price": 100000,
                },
                "minPricePerSquareMeter": {
                    "areaInSquareMeters": 4900,
                    "price": 129000,
                    "pricePerSquareMeter": 26,
                },
            }
        ],
    }
    date = result["searchEvents"][0].pop("date")
    assert date is not None
    assert result == expected_result


@pytest.mark.asyncio
async def test_edit_schedule(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    mocker: MockerFixture,
) -> None:
    category = Category(name="Plot")
    _db_session.add(category)
    await _db_session.commit()
    url = "https://www.test.io/test"
    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)
    resp = MockAioJSONResponse(body, 200)
    mocker.patch("aiohttp.ClientSession.get", return_value=resp)
    mutation = f"""
        mutation adhocScan {{
            adhocScan(input: {{
                    url: "{url}"
                }}) {{
                __typename
                ... on ScanSucceeded {{
                    message
                }}
            }}
        }}
    """
    await authenticated_client.post("/graphql", json={"query": mutation})
    search = (await _db_session.exec(select(Search))).first()
    assert search.schedule is None
    schedule = {"day_of_week": 0, "hour": 1, "minute": 2}
    schedule_mock = mocker.patch("api.schemas.search.setup_scan_periodic_task")
    response = await authenticated_client.post(
        "/graphql",
        json={
            "query": EDIT_SCHEDULE.format(
                id=search.id,
                day=schedule["day_of_week"],
                minute=schedule["minute"],
                hour=schedule["hour"],
            )
        },
    )
    assert (
        response.json()["data"]["editSchedule"]["__typename"]
        == "ScheduleEditedSuccessfully"
    )
    schedule_mock.assert_called_once()
    await _db_session.flush()
    assert search.schedule == schedule


@pytest.mark.asyncio
async def test_delete_schedule(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    mocker: MockerFixture,
) -> None:
    category = Category(name="Plot")
    _db_session.add(category)
    await _db_session.commit()
    url = "https://www.test.io/test"
    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)
    resp = MockAioJSONResponse(body, 200)
    mocker.patch("aiohttp.ClientSession.get", return_value=resp)
    mutation = f"""
        mutation adhocScan {{
            adhocScan(input: {{
                    url: "{url}"
                }}) {{
                __typename
                ... on ScanSucceeded {{
                    message
                }}
            }}
        }}
    """
    await authenticated_client.post("/graphql", json={"query": mutation})
    search = (await _db_session.exec(select(Search))).first()
    schedule = {"day_of_week": 0, "hour": 1, "minute": 2}
    search.schedule = schedule
    _db_session.add(search)
    await _db_session.commit()
    schedule_mock = mocker.patch("api.schemas.search.remove_scan_periodic_task")
    response = await authenticated_client.post(
        "/graphql", json={"query": DELETE_SCHEDULE.format(id=search.id)}
    )
    schedule_mock.assert_called_once()
    assert (
        response.json()["data"]["editSchedule"]["__typename"]
        == "ScheduleEditedSuccessfully"
    )
    await _db_session.flush()
    assert search.schedule is None


@pytest.mark.asyncio
async def test_get_user_list(
    admin_client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    email = "new_user@test.com"
    await admin_client.post(
        "/graphql", json={"query": REGISTER_USER_MUTATION.format(email=email)}
    )
    response = await admin_client.post("/graphql", json={"query": USERS_LIST})
    assert response.status_code == 200
    result = response.json()
    users = result["data"]["allUsers"]["users"]
    assert len(users) == 2
    required_fields = {"email", "id", "isActive", "roles"}
    assert required_fields == set(users[0].keys()) == set(users[1].keys())
    assert email in (user["email"] for user in users)


@pytest.mark.asyncio
async def test_searches_last_status_query(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    add_category: Category,
) -> None:
    search_1 = Search(category=add_category, **examples["search"])
    search_2 = Search(
        **{
            **examples["search"],
            **{"category": add_category, "url": examples["search"]["url"] + "a"},
        }
    )
    search_3 = Search(
        **{
            **examples["search"],
            **{"category": add_category, "url": examples["search"]["url"] + "b"},
        }
    )
    search_4 = Search(
        **{
            **examples["search"],
            **{"category": add_category, "url": examples["search"]["url"] + "c"},
        }
    )
    search_5 = Search(
        **{
            **examples["search"],
            **{"category": add_category, "url": examples["search"]["url"] + "d"},
        }
    )
    estate = Estate(**examples["estate"])
    price = Price(**examples["price"], estate=estate)
    failure_1 = ScanFailure(search=search_2, status_code=404)
    success_1 = SearchEvent(estates=[estate], search=search_3, prices=[price])
    failure_2 = ScanFailure(search=search_4, status_code=404)
    success_2 = SearchEvent(estates=[estate], search=search_4, prices=[price])
    success_3 = SearchEvent(estates=[estate], search=search_5, prices=[price])
    failure_3 = ScanFailure(search=search_5, status_code=404)
    _db_session.add_all(
        [
            search_1,
            search_2,
            search_3,
            search_4,
            search_5,
            failure_1,
            success_1,
            failure_2,
            success_2,
            success_3,
            failure_3,
        ]
    )
    await _db_session.commit()
    _db_session.flush()
    expected = {
        search_1.id: "unknown",
        search_2.id: "failed",
        search_3.id: "success",
        search_4.id: "success",
        search_5.id: "failed",
    }
    response = await authenticated_client.get(
        "/graphql", params={"query": LAST_STATUS_QUERY}
    )
    assert response.status_code == 200
    result = response.json()
    assert len(result["data"]["searchesLastStatus"]["statuses"]) == len(expected.keys())
    for status in result["data"]["searchesLastStatus"]["statuses"]:
        assert expected.get(status["id"]) == status.get("status")

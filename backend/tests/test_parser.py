# type: ignore
import json

import pytest
from dateutil.parser import parse as parse_dt
from pytest_mock import MockerFixture
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.models import Category, Estate, Price, Search, SearchEvent
from api.parsing import parse_scan_data
from api.types.scan import PydanticScanSchedule

SEARCH_EXPECTED = {
    "plot": {
        "coordinates": "neLat: 54.44800258614123, neLng: 18.9510009001242, swLat: "
        "54.27400257787667, swLng: 18.428000875283033",
        "distance_radius": 15,
        "from_price": 100000,
        "from_surface": 100,
        "location": "Gdańsk, pomorskie",
        "to_price": 150000,
        "to_surface": 9999,
    },
    "apartment": {
        "coordinates": "neLat: 50.873298714832345, neLng: 16.52979958242213, swLat: "
        "50.80789871648449, swLng: 16.455299584304157",
        "distance_radius": 0,
        "from_price": 200000,
        "from_surface": 30,
        "location": "Świdnica, świdnicki, dolnośląskie",
        "to_price": 750000,
        "to_surface": 60,
    },
    "house": {
        "coordinates": "neLat: 50.42609872612957, neLng: 16.531299582384236, swLat: "
        "50.371698727503826, swLng: 16.467599583993433",
        "distance_radius": 50,
        "from_price": 150000,
        "from_surface": 30,
        "location": "Polanica-Zdrój, kłodzki, dolnośląskie",
        "to_price": 800000,
        "to_surface": 120,
    },
}

ESTATE_EXPECTED = {
    "plot": {
        "id": 62922460,
        "title": "Działki budowlane Jodłowno gm. Przywidz",
        "street": None,
        "city": "Jodłowno",
        "province": "pomorskie",
        "location": "Jodłowno, pomorskie",
        "date_created": parse_dt("2022-03-27 16:47:38"),
        "url": "dzialki-budowlane-jodlowno-gm-przywidz-ID4g10o",
    },
    "apartment": {
        "id": 64010268,
        "title": "Nowe 3 pok. Klimatyzacja | Garaż | Wysoki Standard",
        "street": "ul. Parkowa",
        "city": "Świdnica",
        "province": "dolnośląskie",
        "location": "ul. Parkowa, Świdnica, dolnośląskie",
        "date_created": parse_dt("2023-03-07 12:08:21"),
        "url": "nowe-3-pok-klimatyzacja-garaz-wysoki-standard-ID4kzZG",
    },
    "house": {
        "id": 64201279,
        "title": "Mały dom z pięknym dużym ogrodem, 3km od Lądka-Zdr",
        "street": None,
        "city": "Radochów",
        "province": "dolnośląskie",
        "location": "Radochów, kłodzki, dolnośląskie",
        "date_created": parse_dt("2023-05-08 15:57:49"),
        "url": "maly-dom-z-pieknym-duzym-ogrodem-3km-od-ladka-zdr-ID4lnGw",
    },
}

PRICE_EXPECTED = {
    "plot": {
        "price": 135000,
        "price_per_square_meter": 135,
        "area_in_square_meters": 1000,
        "terrain_area_in_square_meters": None,
        "estate_id": 62922460,
    },
    "apartment": {
        "price": 620000,
        "price_per_square_meter": 10690,
        "area_in_square_meters": 58,
        "terrain_area_in_square_meters": None,
        "estate_id": 64010268,
    },
    "house": {
        "price": 690000,
        "price_per_square_meter": 7041,
        "area_in_square_meters": 98,
        "terrain_area_in_square_meters": 7289,
        "estate_id": 64201279,
    },
}


@pytest.mark.celery(result_backend="redis://")
@pytest.mark.asyncio
async def test_plot_scan_parsing(
    _db_session: AsyncSession, mocker: MockerFixture
) -> None:
    category = Category(name="Plot")
    _db_session.add(category)
    await _db_session.commit()

    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)

    schedule = PydanticScanSchedule(day_of_week=0, hour=1, minute=2)
    schedule_mock = mocker.patch("api.parsing.setup_scan_periodic_task")
    await parse_scan_data(
        url="https://www.test.io/test",
        body=body,
        session=_db_session,
        schedule=schedule,
    )

    search_parsed = (await _db_session.exec(select(Search))).first()
    for key, value in SEARCH_EXPECTED["plot"].items():
        assert getattr(search_parsed, key) == value

    assert search_parsed.schedule == {"day_of_week": 0, "hour": 1, "minute": 2}
    schedule_mock.assert_called_once()
    search_event_parsed = (await _db_session.exec(select(SearchEvent))).first()
    assert search_event_parsed.search == search_parsed

    estates_parsed = (await _db_session.exec(select(Estate))).all()
    prices_parsed = (await _db_session.exec(select(Price))).all()
    assert len(estates_parsed) == 36
    assert len(prices_parsed) == 36

    expected_estate_data = ESTATE_EXPECTED["plot"]
    estate_parsed = next(
        (estate for estate in estates_parsed if estate.id == expected_estate_data["id"])
    )
    for key, value in expected_estate_data.items():
        assert getattr(estate_parsed, key) == value

    price_parsed = next(
        (
            price
            for price in prices_parsed
            if price.estate_id == expected_estate_data["id"]
        )
    )
    for key, value in PRICE_EXPECTED["plot"].items():
        assert getattr(price_parsed, key) == value


@pytest.mark.asyncio
async def test_apartment_scan_parsing(_db_session: AsyncSession) -> None:
    category = Category(name="Apartment")
    _db_session.add(category)
    await _db_session.commit()

    with open("tests/example_files/body_apartment.json", "r") as f:
        body = json.load(f)

    await parse_scan_data("https://www.test.io/test", body, _db_session)

    search_parsed = (await _db_session.exec(select(Search))).first()
    for key, value in SEARCH_EXPECTED["apartment"].items():
        assert getattr(search_parsed, key) == value

    search_event_parsed = (await _db_session.exec(select(SearchEvent))).first()
    assert search_event_parsed.search == search_parsed

    estates_parsed = (await _db_session.exec(select(Estate))).all()
    prices_parsed = (await _db_session.exec(select(Price))).all()
    assert len(estates_parsed) == 36
    assert len(prices_parsed) == 36

    expected_estate_data = ESTATE_EXPECTED["apartment"]
    estate_parsed = next(
        (estate for estate in estates_parsed if estate.id == expected_estate_data["id"])
    )
    for key, value in expected_estate_data.items():
        assert getattr(estate_parsed, key) == value

    price_parsed = next(
        (
            price
            for price in prices_parsed
            if price.estate_id == expected_estate_data["id"]
        )
    )
    for key, value in PRICE_EXPECTED["apartment"].items():
        assert getattr(price_parsed, key) == value


@pytest.mark.asyncio
async def test_house_scan_parsing(_db_session: AsyncSession) -> None:
    category = Category(name="House")
    _db_session.add(category)
    await _db_session.commit()

    with open("tests/example_files/body_house.json", "r") as f:
        body = json.load(f)

    await parse_scan_data("https://www.test.io/test", body, _db_session)

    search_parsed = (await _db_session.exec(select(Search))).first()
    for key, value in SEARCH_EXPECTED["house"].items():
        assert getattr(search_parsed, key) == value

    search_event_parsed = (await _db_session.exec(select(SearchEvent))).first()
    assert search_event_parsed.search == search_parsed

    estates_parsed = (await _db_session.exec(select(Estate))).all()
    prices_parsed = (await _db_session.exec(select(Price))).all()
    assert len(estates_parsed) == 36
    assert len(prices_parsed) == 36

    expected_estate_data = ESTATE_EXPECTED["house"]
    estate_parsed = next(
        (estate for estate in estates_parsed if estate.id == expected_estate_data["id"])
    )
    for key, value in expected_estate_data.items():
        assert getattr(estate_parsed, key) == value

    price_parsed = next(
        (
            price
            for price in prices_parsed
            if price.estate_id == expected_estate_data["id"]
        )
    )
    for key, value in PRICE_EXPECTED["house"].items():
        assert getattr(price_parsed, key) == value


@pytest.mark.asyncio
async def test_second_scan_parsing(_db_session: AsyncSession) -> None:
    category = Category(name="Plot")
    _db_session.add(category)
    await _db_session.commit()

    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)

    await parse_scan_data("https://www.test.io/test", body, _db_session)
    first_estate = body["pageProps"]["data"]["searchAds"]["items"][0]
    first_estate["title"] = "New Title"
    await parse_scan_data("https://www.test.io/test", body, _db_session)

    serches = (await _db_session.exec(select(Search))).all()
    assert len(serches) == 1
    search_parsed = serches[0]
    for key, value in SEARCH_EXPECTED["plot"].items():
        assert getattr(search_parsed, key) == value

    search_events_parsed = (await _db_session.exec(select(SearchEvent))).all()
    assert len(search_events_parsed) == 2
    assert (
        search_events_parsed[0].search
        == search_events_parsed[1].search
        == search_parsed
    )
    assert search_events_parsed[0].date != search_events_parsed[1].date

    estates_parsed = (await _db_session.exec(select(Estate))).all()
    first_estate_db = next(
        (estate for estate in estates_parsed if estate.id == first_estate["id"])
    )
    assert first_estate_db.title == "New Title"
    prices_parsed = (await _db_session.exec(select(Price))).all()
    assert len(estates_parsed) == 36
    assert len(prices_parsed) == 72

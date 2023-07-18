import pytest
import json
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from api.models import Category, Estate, Search, SearchEvent, Price
from api.parsing import parse_scan_data

search_expected = {
    "coordinates": "neLat: 54.44800258614123, neLng: 18.9510009001242, swLat: "
    "54.27400257787667, swLng: 18.428000875283033",
    "distance_radius": 15,
    "from_price": 100000,
    "from_surface": 100,
    "location": "Gdańsk, pomorskie",
    "to_price": 150000,
    "to_surface": 9999,
}


@pytest.mark.asyncio
async def test_plot_scan_parsing(_db_session: AsyncSession) -> None:
    category = Category(name="Plot")
    _db_session.add(category)
    await _db_session.commit()

    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)

    await parse_scan_data(body, _db_session)

    search_parsed = (await _db_session.exec(select(Search))).first()
    for key, value in search_expected.items():
        assert getattr(search_parsed, key) == value

    search_event_parsed = (await _db_session.exec(select(SearchEvent))).first()
    assert search_event_parsed.search == search_parsed

    estates_parsed = (await _db_session.exec(select(Estate))).all()
    prices_parsed = (await _db_session.exec(select(Price))).all()
    assert len(estates_parsed) == 36
    assert len(prices_parsed) == 0

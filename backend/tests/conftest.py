import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

examples = {
    "category": {"name": "Plot"},
    "search": {
        "location": "London",
        "distance_radius": 10,
        "coordinates": "neLat: 50.474910540541,neLng: 16.720976750824,swLat: 50.393829459459,swLng: 16.593683249176",  # noqa
        "from_price": 10000,
        "to_price": 100000,
        "from_surface": 0,
        "to_surface": 5000,
    },
    "user": {"email": "john@test.com"},
    "estate": {
        "title": "Some great deal",
        "street": "Glowna 31",
        "city": "Pcim Dolny",
        "province": "Podlasie",
        "location": "Podlasie, Pcim Dolny, Glowna 31",
        "url": "www.test.com",
    },
    "price": {
        "price": 100000,
        "price_per_square_meter": 100,
        "area_in_square_meters": 10000,
        "terrain_area_in_square_meters": 10000,
    },
}


@pytest.fixture
def _db_session():
    """Create temporary database for tests"""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

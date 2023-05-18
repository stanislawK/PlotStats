import asyncio
from typing import cast

from faker import Faker
from polyfactory import Ignore, Use
from polyfactory.factories.pydantic_factory import ModelFactory

from api.database import get_async_session
from api.models import Category, Estate, Price, Search, SearchEvent, User


class UserFactory(ModelFactory[User]):
    __model__ = User
    id = Ignore()


class CategoryFactory(ModelFactory[Category]):
    __model__ = Category
    id = Ignore()
    name: str = Use(
        ModelFactory.__random__.choice, choices=["Plot", "Apartment"]
    )  # type: ignore


class SearchFactory(ModelFactory[Search]):
    __model__ = Search
    __faker__ = Faker(locale="pl_PL")
    id = Ignore()

    @classmethod
    def location(cls) -> str:
        return cast(str, cls.__faker__.city())


class EstateFactory(ModelFactory[Estate]):
    __model__ = Estate
    __faker__ = Faker(locale="pl_PL")
    id = Ignore()

    @classmethod
    def title(cls) -> str:
        return cast(str, cls.__faker__.sentence())

    @classmethod
    def street(cls) -> str:
        return cast(str, cls.__faker__.street_address())

    @classmethod
    def city(cls) -> str:
        return cast(str, cls.__faker__.city())

    @classmethod
    def province(cls) -> str:
        return cast(str, cls.__faker__.administrative_unit())

    @classmethod
    def location(cls) -> str:
        return cast(str, cls.__faker__.address())

    @classmethod
    def url(cls) -> str:
        return cast(str, cls.__faker__.url())


class PriceFactory(ModelFactory[Price]):
    __model__ = Price
    id = Ignore()

    price = Use(ModelFactory.__random__.randint, 50000, 500000)
    price_per_square_meter = Use(ModelFactory.__random__.randint, 50, 500)
    area_in_square_meters = Use(ModelFactory.__random__.randint, 200, 10000)


class SearchEventFactory(ModelFactory[SearchEvent]):
    __model__ = SearchEvent
    id = Ignore()


async def main() -> None:
    async for session in get_async_session():
        category = CategoryFactory.build()
        searches = SearchFactory.batch(5, category=category)
        user = UserFactory.build(searches=searches)
        estates = EstateFactory.batch(15)
        prices = []
        for estate in estates:
            prices.append(PriceFactory.build(estate=estate))
        search_event = SearchEventFactory.build(
            estates=estates, search=searches[0], prices=prices
        )

        session.add(user)
        session.add(search_event)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())

from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Column, ForeignKey
from sqlmodel import Field, Relationship, SQLModel

from .estate import Estate

if TYPE_CHECKING:
    from . import SearchEvent


class Price(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    price: int
    price_per_square_meter: Optional[int] = Field(default=None)
    area_in_square_meters: Optional[int] = Field(default=None)
    terrain_area_in_square_meters: Optional[int] = Field(default=None)
    estate_id: Optional[int] = Field(
        default=None, sa_column=Column(BigInteger(), ForeignKey("estate.id"))
    )
    estate: Estate = Relationship(back_populates="prices")
    search_event_id: Optional[int] = Field(default=None, foreign_key="searchevent.id")
    search_event: "SearchEvent" = Relationship(back_populates="prices")

import base64
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel

from . import Category
from .user import SearchUser, User

if TYPE_CHECKING:
    from . import SearchEvent


def encode_url(url: str) -> bytes:
    return base64.urlsafe_b64encode(url.encode("ascii"))


def decode_url(encoded_url: bytes) -> str:
    return base64.urlsafe_b64decode(encoded_url).decode("ascii")


class Search(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category: Optional[Category] = Relationship(back_populates="searches")
    location: str = Field(index=True)
    distance_radius: Optional[int] = Field(default=0)
    coordinates: Optional[str] = Field(default=None)
    from_price: Optional[int]
    to_price: Optional[int]
    from_surface: Optional[int]
    to_surface: Optional[int]
    search_events: List["SearchEvent"] = Relationship(back_populates="search")
    users: List[User] = Relationship(
        back_populates="searches",
        link_model=SearchUser,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    url: str = Field(index=True, unique=True)
    schedule: Optional[dict[str, int]] = Field(sa_column=Column(JSON), default=None)

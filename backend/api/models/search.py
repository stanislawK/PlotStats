from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from . import Category
from .user import User, SearchUser

if TYPE_CHECKING:
    from . import SearchEvent


class Search(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category: Optional[Category] = Relationship(back_populates="searches")
    location: str = Field(index=True)
    distance_radius: int = Field(default=0)
    coordinates: Optional[str] = Field(default=None)
    from_price: Optional[int]
    to_price: Optional[int]
    from_surface: Optional[int]
    to_surface: Optional[int]
    search_events: List["SearchEvent"] = Relationship(back_populates="search")
    users: List[User] = Relationship(back_populates="searches", link_model=SearchUser)

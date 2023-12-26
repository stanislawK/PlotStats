from typing import Annotated, Union

import strawberry

from api.models.user import User
from api.types.general import Error, InputValidationError


@strawberry.type
class JWTPair:
    access_token: str
    refresh_token: str


@strawberry.type
class AccessToken:
    access_token: str


@strawberry.experimental.pydantic.input(model=User)
class LoginUserData:
    email: strawberry.auto
    password: strawberry.auto


@strawberry.type
class LoginUserError(Error):
    message: str = "Login user error"


@strawberry.type
class RefreshTokenError(Error):
    message: str = "Refresh token error"


LoginUserResponse = Annotated[
    Union[JWTPair, LoginUserError, InputValidationError],
    strawberry.union("LoginUserResponse"),
]

RefreshTokenResponse = Annotated[
    Union[AccessToken, RefreshTokenError],
    strawberry.union("RefreshTokenResponse"),
]

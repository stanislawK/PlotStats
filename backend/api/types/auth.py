from typing import Annotated, Union

import strawberry
from pydantic import BaseModel, EmailStr

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


class UserEmail(BaseModel):
    email: EmailStr


@strawberry.experimental.pydantic.input(model=UserEmail, all_fields=True)
class NewUserInput:
    pass


@strawberry.type
class RegisterResponse:
    temporary_password: str


@strawberry.type
class UserExistsError(Error):
    message: str = "User with that email already exists"


LoginUserResponse = Annotated[
    Union[JWTPair, LoginUserError, InputValidationError],
    strawberry.union("LoginUserResponse"),
]

RefreshTokenResponse = Annotated[
    Union[AccessToken, RefreshTokenError],
    strawberry.union("RefreshTokenResponse"),
]

RegisterUserResponse = Annotated[
    Union[RegisterResponse, UserExistsError, InputValidationError],
    strawberry.union("RegisterUserResponse"),
]

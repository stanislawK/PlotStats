import re
from typing import Annotated, Union

import strawberry
from pydantic import BaseModel, EmailStr, constr, field_validator, model_validator

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


@strawberry.experimental.pydantic.input(model=UserEmail, all_fields=True)
class DeactivateUserInput:
    pass


@strawberry.type
class DeactivateAccountSuccess:
    message: str = "Deactivated account successfully"


@strawberry.type
class RegisterResponse:
    temporary_password: str


class ActivateAccount(BaseModel):
    email: EmailStr
    temp_password: str
    new_password: constr(min_length=8, max_length=50)  # type: ignore

    @field_validator("new_password")
    @classmethod
    def regex_match(cls, password: str) -> str:
        re_for_new_password: re.Pattern[str] = re.compile(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"
            r"(?=.*[@$!%*?&#\.\^/<>\?])"
            r"[A-Za-z\d@$!%*?&#\.\^/<>\?]+$"
        )
        if not re_for_new_password.match(password):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, one digit, and one special character"
            )
        return password

    @model_validator(mode="after")
    def check_password_not_the_same(self) -> "ActivateAccount":
        if self.temp_password == self.new_password:
            raise ValueError("New password cannot be the same as temporary password")
        return self


@strawberry.experimental.pydantic.input(model=ActivateAccount, all_fields=True)
class ActivateAccountInput:
    pass


@strawberry.type
class UserExistsError(Error):
    message: str = "User with that email already exists"


@strawberry.type
class ActivateAccountError(Error):
    message: str = "Activation error"


@strawberry.type
class DeactivateAccountError(Error):
    message: str = "Deactivation error"


@strawberry.type
class ActivateAccountSuccess:
    message: str = "Activated account successfully"


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

DeactivateUserResponse = Annotated[
    Union[DeactivateAccountSuccess, DeactivateAccountError, InputValidationError],
    strawberry.union("DeactivateUserResponse"),
]

ActivateAccountResponse = Annotated[
    Union[ActivateAccountSuccess, ActivateAccountError, InputValidationError],
    strawberry.union("ActivateAccountResponse"),
]

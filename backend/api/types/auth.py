import strawberry

from api.models.user import User
from api.types.general import Error, InputValidationError


@strawberry.type
class JWTPair:
    access_token: str
    refresh_token: str


@strawberry.experimental.pydantic.input(model=User, fields=["email", "password"])
class LoginUserData:
    pass


@strawberry.type
class LoginUserError(Error):
    message: str = "Login user error"


LoginUserResponse = strawberry.union(
    "LoginUserResponse", (JWTPair, LoginUserError, InputValidationError)
)

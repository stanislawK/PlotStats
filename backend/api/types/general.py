import strawberry


@strawberry.interface
class Error:
    message: str

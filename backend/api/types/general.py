import strawberry


@strawberry.interface
class Error:
    message: str


@strawberry.type
class InputValidationError(Error):
    pass

from fastapi import HTTPException
from uuid import UUID
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class UserError(HTTPException):
    # Base class for all user errors
    pass


class EventError(HTTPException):
    # Base class for all order errors
    pass


class AudioError(HTTPException):
    # Base class for all audio errors
    pass


class UserNotFoundError(UserError):
    def __init__(self, user_id: None):
        message = (
            "User not found" if user_id is None else f"User with id {user_id} not found"
        )
        super().__init__(status_code=404, detail=message)


class PasswordMismatchError(UserError):
    def __init__(self):
        super().__init__(status_code=400, detail="Password mismatch")


class InvalidPasswordError(UserError):
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid password")


class AuthenticationError(UserError):
    def __init__(self, message: str = "Authentication error"):
        super().__init__(status_code=401, detail=message)


class UserAlreadyExistsError(UserError):
    def __init__(self, email: str):
        super().__init__(
            status_code=400, detail=f"User with email {email} already exists"
        )


class EventNotFoundError(EventError):
    def __init__(self, event_id: UUID):
        super().__init__(status_code=404, detail=f"Event with id {event_id} not found")


class AudioNotFoundError(AudioError):
    def __init__(self, audio_id: UUID):
        super().__init__(status_code=404, detail=f"Audio with id {audio_id} not found")


class AudioNotProcessedError(AudioError):
    def __init__(self, audio_id: UUID):
        super().__init__(
            status_code=400, detail=f"Audio {audio_id} is not processed yet"
        )


class AudioAlreadyAttachedError(AudioError):
    def __init__(self, audio_id: UUID):
        super().__init__(
            status_code=400, detail=f"Audio {audio_id} is already attached to an event"
        )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(UserError)
    @app.exception_handler(EventError)
    @app.exception_handler(AudioError)
    async def custom_http_exception_handler(
        request: Request, exc: UserError | EventError | AudioError
    ):
        error_name = getattr(exc, "error", exc.__class__.__name__)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status_code": exc.status_code,
                "error": error_name,
                "message": exc.detail,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status_code": exc.status_code,
                "error": exc.__class__.__name__,
                "message": exc.detail,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        return JSONResponse(
            status_code=422,
            content={
                "status_code": 422,
                "error": "ValidationError",
                "message": "Validation error",
            },
        )

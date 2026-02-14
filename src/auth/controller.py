from fastapi import APIRouter, status, Body, Request, Response, Cookie
from . import service
from ..database.database import DbSession
from ..rate_limiting import limiter
from .schemas import (
    RegisterUserRequest,
    LoginRequest,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
@limiter.limit("5/hour")
async def register_user(
    request: Request,
    db: DbSession,
    response: Response,
    register_user_request: RegisterUserRequest = Body(...),
):
    return service.register_user(db, response, register_user_request)


@router.post("/login", response_model=UserResponse)
async def login(login_request: LoginRequest, db: DbSession, response: Response):
    return service.login(login_request, db, response)


@router.post("/refresh")
async def refresh_access_token(
    db: DbSession,
    response: Response,
    refresh_token: str | None = Cookie(None),
):
    return service.refresh_access_token(db, refresh_token, response)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(current_user: service.CurrentUser, db: DbSession, response: Response):
    user_id = current_user.get_uuid()
    if user_id is None:
        raise service.AuthenticationError("Invalid user id in token")
    service.revoke_refresh_tokens_for_user(db, user_id)

    # Clear cookies
    response.delete_cookie(
        key="access_token", httponly=True, secure=False, samesite="lax"
    )
    response.delete_cookie(
        key="refresh_token", httponly=True, secure=False, samesite="lax"
    )

    return {"message": "Logged out"}

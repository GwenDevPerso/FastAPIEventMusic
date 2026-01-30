from fastapi import APIRouter, status, Body, Request
from . import service
from ..database.database import DbSession
from ..rate_limiting import limiter
from .schemas import (
    RegisterUserRequest,
    LoginRequest,
    UserWithTokenResponse,
    TokenResponse,
    RefreshTokenRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/hour")
async def register_user(
    request: Request,
    db: DbSession,
    register_user_request: RegisterUserRequest = Body(...),
):
    return service.register_user(db, register_user_request)


@router.post("/login", response_model=UserWithTokenResponse)
async def login(request: LoginRequest, db: DbSession):
    return service.login(request, db)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(request: RefreshTokenRequest, db: DbSession):
    return service.refresh_access_token(db, request.refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(current_user: service.CurrentUser, db: DbSession):
    user_id = current_user.get_uuid()
    if user_id is None:
        raise service.AuthenticationError("Invalid user id in token")
    service.revoke_refresh_tokens_for_user(db, user_id)
    return {"message": "Logged out"}

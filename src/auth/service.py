from __future__ import annotations

from datetime import timedelta, datetime, timezone
import hashlib
import secrets
from typing import Annotated
from fastapi import Depends
from uuid import UUID, uuid4
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError
from sqlalchemy.orm import Session
from src.users.models import User
from .models import RefreshToken
from .schemas import (
    RegisterUserRequest,
    LoginRequest,
    UserWithTokenResponse,
    TokenResponse,
    UserResponse,
    TokenData,
)
from fastapi.security import OAuth2PasswordBearer
from ..exceptions import AuthenticationError, UserAlreadyExistsError
import logging
import os

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)


def authenticate_user(email: str, password: str, db: Session) -> User | bool:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        logging.warning(f"Invalid email or password for user {email}")
        return False
    return user


def create_access_token(email: str, user_id: UUID, expires_delta: timedelta) -> str:
    encode = {
        "sub": email,
        "id": str(user_id),
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    return jwt.encode(encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))


def _hash_refresh_token(refresh_token: str) -> str:
    return hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()


def _build_refresh_token(user_id: UUID, now: datetime) -> tuple[str, RefreshToken]:
    raw_refresh_token = secrets.token_urlsafe(48)
    refresh_token = RefreshToken(
        id=uuid4(),
        user_id=user_id,
        token_hash=_hash_refresh_token(raw_refresh_token),
        created_at=now,
        expires_at=now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        revoked_at=None,
        replaced_by_token_id=None,
    )
    return raw_refresh_token, refresh_token


def revoke_refresh_tokens_for_user(db: Session, user_id: UUID) -> None:
    now = datetime.now(timezone.utc)
    (
        db.query(RefreshToken)
        .filter(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .update({"revoked_at": now}, synchronize_session=False)
    )
    db.commit()


def refresh_access_token(db: Session, refresh_token: str) -> TokenResponse:
    now = datetime.now(timezone.utc)
    refresh_token_hash = _hash_refresh_token(refresh_token)

    stored_refresh_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == refresh_token_hash)
        .first()
    )

    if (
        stored_refresh_token is None
        or stored_refresh_token.revoked_at is not None
        or stored_refresh_token.expires_at <= now
    ):
        raise AuthenticationError("Refresh token is invalid or expired")

    user = db.query(User).filter(User.id == stored_refresh_token.user_id).first()
    if not user:
        raise AuthenticationError("User not found for refresh token")

    stored_refresh_token.revoked_at = now

    new_raw_refresh_token, new_refresh_token = _build_refresh_token(user.id, now)
    stored_refresh_token.replaced_by_token_id = new_refresh_token.id

    db.add(new_refresh_token)
    db.commit()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.email, user.id, access_token_expires)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_raw_refresh_token,
        token_type="bearer",
    )


def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
        user_id: str = payload.get("id")
        return TokenData(user_id=user_id)
    except PyJWTError:
        logging.warning(f"Could not validate credentials for token {token}")
        raise AuthenticationError(
            "Could not validate credentials, the token is invalid or expired"
        )


def register_user(
    db: Session, register_user_request: RegisterUserRequest
) -> UserWithTokenResponse:
    try:
        if db.query(User).filter(User.email == register_user_request.email).first():
            logging.warning(
                f"User with email {register_user_request.email} already exists"
            )
            raise UserAlreadyExistsError(f"{register_user_request.email}")
        user = User(
            id=uuid4(),
            email=register_user_request.email,
            first_name=register_user_request.first_name,
            last_name=register_user_request.last_name,
            password=get_password_hash(register_user_request.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(user.email, user.id, access_token_expires)

        now = datetime.now(timezone.utc)
        raw_refresh_token, refresh_token = _build_refresh_token(user.id, now)
        db.add(refresh_token)
        db.commit()

        return UserWithTokenResponse(
            user=UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                created_at=user.created_at,
            ),
            token=TokenResponse(
                access_token=access_token,
                refresh_token=raw_refresh_token,
                token_type="bearer",
            ),
        )
    except Exception as e:
        logging.error(f"Error registering user: {e}")
        raise e


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]) -> TokenData:
    return verify_token(token)


CurrentUser = Annotated[TokenData, Depends(get_current_user)]


def login(login_request: LoginRequest, db: Session) -> UserWithTokenResponse:
    user = authenticate_user(login_request.email, login_request.password, db)
    if not user:
        raise AuthenticationError("Invalid email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.email, user.id, access_token_expires)

    now = datetime.now(timezone.utc)
    raw_refresh_token, refresh_token = _build_refresh_token(user.id, now)
    db.add(refresh_token)
    db.commit()

    return UserWithTokenResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            created_at=user.created_at,
        ),
        token=TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh_token,
            token_type="bearer",
        ),
    )

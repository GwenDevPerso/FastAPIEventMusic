from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr
from src.users.schemas import UserResponse


class RegisterUserRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class UserWithTokenResponse(BaseModel):
    user: UserResponse
    token: TokenResponse


class TokenData(BaseModel):
    user_id: Optional[str] = None

    def get_uuid(self) -> Optional[UUID]:
        if self.user_id:
            return UUID(self.user_id)
        return None


class RefreshTokenRequest(BaseModel):
    refresh_token: str

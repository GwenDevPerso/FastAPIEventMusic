from uuid import UUID
from sqlalchemy.orm import Session
from .schemas import UserResponse, PasswordChangeRequest
from .models import User
from src.exceptions import (
    UserNotFoundError,
    InvalidPasswordError,
    PasswordMismatchError,
)
from src.auth.service import verify_password, get_password_hash
import logging


def get_user_by_id(db: Session, user_id: UUID) -> UserResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logging.warning(f"User with id {user_id} not found")
        raise UserNotFoundError(f"User with id {user_id} not found")
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        created_at=user.created_at,
    )


def change_password(
    db: Session, user_id: UUID, password_change: PasswordChangeRequest
) -> None:
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logging.warning(f"User with id {user_id} not found")
            raise UserNotFoundError(f"User with id {user_id} not found")

        # Verify current password
        if not verify_password(password_change.current_password, user.password):
            logging.warning(f"Invalid current password for user {user_id}")
            raise InvalidPasswordError(f"Invalid current password for user {user_id}")

        # Verify new password
        if password_change.new_password != password_change.new_password_confirm:
            logging.warning(
                f"New password and confirm password do not match for user {user_id}"
            )
            raise PasswordMismatchError(
                f"New password and confirm password do not match for user {user_id}"
            )

        # Update password
        user.password = get_password_hash(password_change.new_password)
        db.commit()
        logging.info(f"Password changed successfully for user {user_id}")
    except Exception as e:
        logging.error(f"Error changing password for user {user_id}: {e}")
        raise e

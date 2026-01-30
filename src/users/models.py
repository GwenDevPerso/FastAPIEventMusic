from sqlalchemy import Column, String, DateTime, UUID
from datetime import datetime
from ..database.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(UUID, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"User(id={self.id}, email={self.email}, first_name={self.first_name}, last_name={self.last_name}, created_at={self.created_at}, updated_at={self.updated_at})"

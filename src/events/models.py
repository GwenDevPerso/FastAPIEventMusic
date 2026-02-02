from sqlalchemy import Column, String, DateTime, UUID, Enum
from datetime import datetime
from enum import StrEnum
from ..database.database import Base
from uuid import uuid4
from sqlalchemy.orm import relationship


class EventStatus(StrEnum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"


class Event(Base):
    __tablename__ = "events"
    id = Column(UUID, primary_key=True, index=True, default=uuid4)
    name = Column(String)
    status = Column(Enum(EventStatus), default=EventStatus.DRAFT)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    audios = relationship("Audio", back_populates="event")

    def __repr__(self):
        return f"Event(id={self.id}, name={self.name}, status={self.status}, created_at={self.created_at}, updated_at={self.updated_at})"

from sqlalchemy import Column, String, DateTime, UUID, Enum, Integer, ForeignKey
from datetime import datetime
from enum import StrEnum
from ..database.database import Base
from uuid import uuid4


class EventStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class Event(Base):
    __tablename__ = "events"
    id = Column(UUID, primary_key=True, index=True, default=uuid4)
    name = Column(String)
    status = Column(Enum(EventStatus), default=EventStatus.PENDING)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"Event(id={self.id}, name={self.name}, status={self.status}, created_at={self.created_at}, updated_at={self.updated_at})"


class TrackPlay(Base):
    __tablename__ = "track_plays"

    id = Column(UUID, primary_key=True)
    event_id = Column(UUID, ForeignKey("events.id"), nullable=False)
    artist = Column(String, nullable=False)
    title = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)

    def __repr__(self):
        return f"TrackPlay(id={self.id}, event_id={self.event_id}, artist={self.artist!r}, title={self.title!r}, duration={self.duration})"

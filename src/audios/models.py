from sqlalchemy import Column, String, DateTime, UUID, Enum, Integer, ForeignKey
from datetime import datetime
from enum import StrEnum
from ..database.database import Base
from uuid import uuid4
from sqlalchemy.orm import relationship
from sqlalchemy.types import LargeBinary


class AudioStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class Audio(Base):
    __tablename__ = "audios"
    id = Column(UUID, primary_key=True, index=True, default=uuid4)
    name = Column(String)
    status = Column(Enum(AudioStatus), default=AudioStatus.PENDING)
    file = Column(LargeBinary, nullable=False)
    event_id = Column(UUID, ForeignKey("events.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    track_plays = relationship("TrackPlay", back_populates="audio")
    event = relationship("Event", back_populates="audios")

    def __repr__(self):
        return f"Audio(id={self.id}, name={self.name}, status={self.status}, created_at={self.created_at}, updated_at={self.updated_at})"


class TrackPlay(Base):
    __tablename__ = "track_plays"

    id = Column(UUID, primary_key=True, default=uuid4)
    audio_id = Column(UUID, ForeignKey("audios.id"), nullable=False, index=True)
    artist = Column(String, nullable=False)
    title = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)

    audio = relationship("Audio", back_populates="track_plays")

    def __repr__(self):
        return f"TrackPlay(id={self.id}, audio_id={self.audio_id}, artist={self.artist!r}, title={self.title!r}, duration={self.duration})"

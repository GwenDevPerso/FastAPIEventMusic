from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from .models import AudioStatus


class TrackPlayReadResponse(BaseModel):
    id: UUID
    audio_id: UUID
    artist: str
    title: str
    duration: int


class AudioReadResponse(BaseModel):
    id: UUID
    name: str
    status: AudioStatus
    event_id: UUID | None
    created_at: datetime
    updated_at: datetime
    track_plays: list[TrackPlayReadResponse]

    class Config:
        from_attributes = True

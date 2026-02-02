from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from .models import EventStatus


class EventCreateRequest(BaseModel):
    name: str
    audio_ids: list[UUID]


class EventReadResponse(BaseModel):
    id: UUID
    name: str
    status: EventStatus
    audio_ids: list[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from .models import EventStatus


class EventCreateRequest(BaseModel):
    name: str


class EventReadResponse(BaseModel):
    id: UUID
    name: str
    status: EventStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

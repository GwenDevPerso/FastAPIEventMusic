from ..database.database import DbSession
from .schemas import EventCreateRequest, EventReadResponse
from .models import Event, EventStatus
from src.audios.models import Audio, AudioStatus
from src.exceptions import AudioAlreadyAttachedError, AudioNotFoundError, AudioNotProcessedError
from uuid import uuid4


def create(db: DbSession, event_request: EventCreateRequest) -> EventReadResponse:
    event = Event(id=uuid4(), name=event_request.name, status=EventStatus.DRAFT)
    db.add(event)
    db.commit()
    db.refresh(event)

    for audio_id in event_request.audio_ids:
        audio = db.query(Audio).filter(Audio.id == audio_id).first()
        if not audio:
            raise AudioNotFoundError(audio_id)
        if audio.status != AudioStatus.PROCESSED:
            raise AudioNotProcessedError(audio_id)
        if audio.event_id is not None:
            raise AudioAlreadyAttachedError(audio_id)
        audio.event_id = event.id

    db.commit()
    db.refresh(event)
    return EventReadResponse(
        id=event.id,
        name=event.name,
        status=event.status,
        audio_ids=[audio.id for audio in event.audios],
        created_at=event.created_at,
        updated_at=event.updated_at,
    )


def get_all(db: DbSession) -> list[EventReadResponse]:
    events = db.query(Event).all()
    return [
        EventReadResponse(
            id=event.id,
            name=event.name,
            status=event.status,
            audio_ids=[audio.id for audio in event.audios],
            created_at=event.created_at,
            updated_at=event.updated_at,
        )
        for event in events
    ]

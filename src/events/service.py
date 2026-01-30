from ..database.database import DbSession
from .schemas import EventCreateRequest, EventReadResponse
from .models import Event, EventStatus
from src.exceptions import EventNotFoundError
from uuid import UUID, uuid4
from .tasks import process_event_audio


def create(db: DbSession, event: EventCreateRequest) -> EventReadResponse:
    event = Event(id=uuid4(), name=event.name)
    db.add(event)
    db.commit()
    db.refresh(event)
    return EventReadResponse(
        id=event.id,
        name=event.name,
        status=event.status,
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
            created_at=event.created_at,
            updated_at=event.updated_at,
        )
        for event in events
    ]


def process(db: DbSession, event_id: UUID) -> dict:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise EventNotFoundError(event_id)
    event.status = EventStatus.PROCESSING
    db.commit()
    db.refresh(event)

    # Send task to process event audio to celery worker
    process_event_audio.delay(event_id)
    return {"status": "processing"}

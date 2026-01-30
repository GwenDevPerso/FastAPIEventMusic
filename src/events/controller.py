from fastapi import APIRouter
from .schemas import EventReadResponse
from ..database.database import DbSession
from .schemas import EventCreateRequest
from . import service
from fastapi import status
from uuid import UUID

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventReadResponse)
async def create(event: EventCreateRequest, db: DbSession):
    return service.create(db, event)


@router.get("/", response_model=list[EventReadResponse])
async def get_all(db: DbSession):
    return service.get_all(db)


@router.post("/{event_id}/process", status_code=status.HTTP_200_OK)
async def process(event_id: UUID, db: DbSession):
    return service.process(db, event_id)

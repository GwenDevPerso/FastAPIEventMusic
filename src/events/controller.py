from fastapi import APIRouter
from .schemas import EventReadResponse
from ..database.database import DbSession
from .schemas import EventCreateRequest
from . import service
from src.auth.service import CurrentUser

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventReadResponse)
async def create(event: EventCreateRequest, db: DbSession, current_user: CurrentUser):
    return service.create(db, event)


@router.get("/", response_model=list[EventReadResponse])
async def get_all(db: DbSession, current_user: CurrentUser):
    return service.get_all(db)

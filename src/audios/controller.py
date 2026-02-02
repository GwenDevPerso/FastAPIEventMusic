from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile
from uuid import UUID

from ..database.database import DbSession
from .schemas import AudioReadResponse
from . import service
from src.auth.service import CurrentUser

router = APIRouter(prefix="/audios", tags=["audios"])


@router.post("/", response_model=AudioReadResponse)
async def create(
    db: DbSession,
    current_user: CurrentUser,
    name: Annotated[str, Form(...)],
    file: Annotated[UploadFile, File(...)],
):
    file_bytes = await file.read()
    return service.create(db=db, name=name, file=file_bytes)


@router.get("/", response_model=list[AudioReadResponse])
async def get_all(db: DbSession):
    return service.get_all(db)


@router.get("/{audio_id}", response_model=AudioReadResponse)
async def get_by_id(audio_id: UUID, db: DbSession, current_user: CurrentUser):
    return service.get_by_id(db=db, audio_id=audio_id)

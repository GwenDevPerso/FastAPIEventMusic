from ..database.database import DbSession
from .schemas import AudioReadResponse, TrackPlayReadResponse
from .models import Audio, AudioStatus
from uuid import UUID, uuid4
from .tasks import process_audio
from sqlalchemy.orm import selectinload
from src.exceptions import AudioNotFoundError


def create(db: DbSession, name: str, file: bytes) -> AudioReadResponse:
    audio = Audio(id=uuid4(), name=name, file=file, status=AudioStatus.PENDING)
    db.add(audio)
    db.commit()
    db.refresh(audio)

    process_audio.delay(str(audio.id))
    return AudioReadResponse(
        id=audio.id,
        name=audio.name,
        status=audio.status,
        event_id=audio.event_id,
        created_at=audio.created_at,
        updated_at=audio.updated_at,
    )


def get_by_id(db: DbSession, audio_id: UUID) -> AudioReadResponse:
    audio = db.query(Audio).filter(Audio.id == audio_id).first()
    if not audio:
        raise AudioNotFoundError(audio_id)
    return AudioReadResponse(
        id=audio.id,
        name=audio.name,
        status=audio.status,
        event_id=audio.event_id,
        created_at=audio.created_at,
        updated_at=audio.updated_at,
        track_plays=[
            TrackPlayReadResponse(
                id=track_play.id,
                audio_id=track_play.audio_id,
                artist=track_play.artist,
                title=track_play.title,
                duration=track_play.duration,
            )
            for track_play in audio.track_plays
        ],
    )


def get_all(db: DbSession) -> list[AudioReadResponse]:
    audios = db.query(Audio).options(selectinload(Audio.track_plays)).all()
    return [
        AudioReadResponse(
            id=audio.id,
            name=audio.name,
            status=audio.status,
            event_id=audio.event_id,
            created_at=audio.created_at,
            updated_at=audio.updated_at,
            track_plays=[
                TrackPlayReadResponse(
                    id=track_play.id,
                    audio_id=track_play.audio_id,
                    artist=track_play.artist,
                    title=track_play.title,
                    duration=track_play.duration,
                )
                for track_play in audio.track_plays
            ],
        )
        for audio in audios
    ]

import json
from uuid import UUID, uuid4

from redis import Redis
from sqlalchemy.orm import selectinload

from ..database.database import DbSession
from .models import Audio, AudioStatus
from .schemas import AudioReadResponse, TrackPlayReadResponse
from .tasks import process_audio
from src.exceptions import AudioNotFoundError
from src.core.redis import AUDIOS_LIST_CACHE_KEY, AUDIOS_LIST_CACHE_TTL_SECONDS


def create(db: DbSession, redis: Redis, name: str, file: bytes) -> AudioReadResponse:
    audio = Audio(id=uuid4(), name=name, file=file, status=AudioStatus.PENDING)
    db.add(audio)
    db.commit()
    db.refresh(audio)

    response = AudioReadResponse(
        id=audio.id,
        name=audio.name,
        status=audio.status,
        event_id=audio.event_id,
        created_at=audio.created_at,
        updated_at=audio.updated_at,
        track_plays=[],
    )
    process_audio.delay(str(audio.id))
    redis.delete(AUDIOS_LIST_CACHE_KEY)
    return response


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


def get_all(db: DbSession, redis: Redis) -> list[AudioReadResponse]:
    cached = redis.get(AUDIOS_LIST_CACHE_KEY)
    if cached is not None:
        return [AudioReadResponse.model_validate(obj) for obj in json.loads(cached)]

    audios = db.query(Audio).options(selectinload(Audio.track_plays)).all()
    responses = [
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
    redis.set(
        AUDIOS_LIST_CACHE_KEY,
        json.dumps([r.model_dump(mode="json") for r in responses]),
        ex=AUDIOS_LIST_CACHE_TTL_SECONDS,
    )
    return responses

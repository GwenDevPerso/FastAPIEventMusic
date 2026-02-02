from src.core.celery import celery_app
from src.database.database import SessionLocal
from uuid import UUID
import time

from src.audios.models import Audio, AudioStatus, TrackPlay


@celery_app.task
def process_audio(audio_id: str):
    db = SessionLocal()
    try:
        audio_uuid = UUID(audio_id)
        audio = db.query(Audio).filter(Audio.id == audio_uuid).first()
        if not audio:
            raise ValueError(f"Audio not found: {audio_id}")

        time.sleep(3)  # simulate audio processing

        tracks = [
            TrackPlay(
                audio_id=audio_uuid,
                artist="Daft Punk",
                title="One More Time",
                duration=320,
            ),
            TrackPlay(
                audio_id=audio_uuid,
                artist="Justice",
                title="D.A.N.C.E.",
                duration=250,
            ),
        ]
        db.add_all(tracks)
        audio.status = AudioStatus.PROCESSED
        db.commit()
        return {"audio_id": audio_id, "tracks": len(tracks)}
    except Exception as e:
        db.rollback()
        if audio is not None:
            audio.status = AudioStatus.FAILED
            db.commit()
        raise e
    finally:
        db.close()

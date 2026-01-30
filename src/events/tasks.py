# events/tasks.py
from src.core.celery import celery_app
from src.events.models import TrackPlay
from src.database.database import SessionLocal
from uuid import UUID
import time


@celery_app.task
def process_event_audio(event_id: UUID):
    db = SessionLocal()
    time.sleep(3)  # simulation traitement audio
    # création mock des tracks
    tracks = [
        TrackPlay(
            event_id=event_id, artist="Daft Punk", title="One More Time", duration=320
        ),
        TrackPlay(
            event_id=event_id, artist="Justice", title="D.A.N.C.E.", duration=250
        ),
    ]
    db.add_all(tracks)
    db.commit()
    db.close()
    return {"event_id": event_id, "tracks": len(tracks)}

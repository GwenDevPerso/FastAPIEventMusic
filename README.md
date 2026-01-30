┌─────────────┐
│   Client    │ POST /events/{id}/process
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  FastAPI App    │ controller.process()
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  service.py     │ 1. Update DB: status = PROCESSING
│  process()      │ 2. process_event_audio.delay()
└──────┬──────────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌─────────────┐   ┌──────────────┐
│ PostgreSQL  │   │ Redis Broker │ ← Queue de tâches
│   (Event)   │   └──────┬───────┘
└─────────────┘          │
                         ▼
                  ┌──────────────┐
                  │Celery Worker │ ← Traite la tâche
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  tasks.py    │ process_event_audio()
                  │              │ - Traite audio
                  │              │ - Crée TrackPlay
                  └──────┬───────┘
                         │
                         ├─────────────────┐
                         │                 │
                         ▼                 ▼
                  ┌─────────────┐  ┌──────────────┐
                  │ PostgreSQL  │  │Redis Backend │ ← Résultat
                  │ (TrackPlay) │  └──────────────┘
                  └─────────────┘# FastAPIEventMusic
# FastAPIEventMusic

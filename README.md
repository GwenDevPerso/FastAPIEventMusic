┌─────────────┐
│   Client    │
└──────┬──────┘
       │ 1) Upload audio (multipart/form-data)
       │    POST /audios/   (name, file)
       ▼
┌─────────────────┐
│  FastAPI App    │ audios.controller.create()
└──────┬──────────┘
       ▼
┌───────────────────────────┐
│ audios.service.create()   │
│ - INSERT audios           │  Audio.status = PROCESSING
│ - COMMIT                  │
│ - enqueue Celery task     │  process_audio.delay(audio_id)
└──────┬────────────────────┘
       │
       ├───────────────┐
       │               │
       ▼               ▼
┌─────────────┐  ┌──────────────┐
│ PostgreSQL  │  │ Redis Broker  │  (queue)
│ tables:     │  └──────┬───────┘
│ - audios    │         ▼
│ - track_plays│  ┌──────────────┐
│ - events    │  │ Celery Worker │
└─────────────┘  └──────┬───────┘
                         ▼
                  ┌──────────────────────┐
                  │ audios.tasks         │
                  │ process_audio(id):   │
                  │ - SELECT audio       │
                  │ - INSERT track_plays │
                  │ - UPDATE audio       │  Audio.status = PROCESSED
                  │ - COMMIT             │
                  └──────────┬───────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Client polling  │
                    │ GET /audios/{id}│ -> AudioReadResponse (status)
                    └─────────────────┘


from fastapi import FastAPI
from .database.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from .core.router import register_routes
from .logging import configure_logging, LogLevels
import logging
from .exceptions import register_exception_handlers

from .users.models import User  # noqa: F401
from .auth.models import RefreshToken  # noqa: F401
from .audios.models import Audio, TrackPlay  # noqa: F401
from .events.models import Event  # noqa: F401

configure_logging(LogLevels.info)

# # Create all tables
Base.metadata.create_all(bind=engine)
logging.info("Tables created")

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

register_exception_handlers(app)
register_routes(app)

from fastapi import FastAPI

from src.users.controller import router as users_router
from src.auth.controller import router as auth_router
from src.events.controller import router as events_router


def register_routes(app: FastAPI):
    app.include_router(users_router)
    app.include_router(auth_router)
    app.include_router(events_router)

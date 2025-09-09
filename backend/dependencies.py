from settings import Settings, get_settings
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_session

"""
dependencies.py

Defines common dependency injection types used across the application.

- SettingsDep:
    Injects the application settings object (from get_settings)
    into routes and services.

- SessionDep:
    Injects a SQLAlchemy Session (from get_session) into routes and services.
    The session is automatically closed after the request.
"""
SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[Session, Depends(get_session)]
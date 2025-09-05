from settings import Settings, get_settings
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_session

SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[Session, Depends(get_session)]
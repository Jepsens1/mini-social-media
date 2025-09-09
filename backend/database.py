from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from settings import get_settings

"""
database.py

Provides the SQLAlchemy database configuration for the application.

Responsibilities:
- Configure the SQLAlchemy engine (based on DATABASE_URL from settings)
- Define the declarative base class for ORM models
- Provide a session factory (SessionLocal) for database access
- Expose a dependency function (get_session) for FastAPI routes
"""
settings = get_settings()

#sqlite_file_name = "database.db"
#sqlite_url = f"sqlite:///{sqlite_file_name}"

#connect_args = {"check_same_thread": False}
engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()

def get_session():
    """
    Dependency that provides a database session.

    Usage:
        Add as a dependency in FastAPI endpoints/services:
        
        def endpoint(session: Annotated[Session, Depends(get_session)]):
            ...
    
    The session is automatically closed after the request.
    """
    with SessionLocal() as session:
        yield session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from settings import get_settings


settings = get_settings()

#sqlite_file_name = "database.db"
#sqlite_url = f"sqlite:///{sqlite_file_name}"

#connect_args = {"check_same_thread": False}
engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()

def create_db_and_tables():
    Base.metadata.create_all(engine)

def get_session():
    with SessionLocal() as session:
        yield session

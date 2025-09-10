from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

"""
settings.py

Defines a Settings class using Pydantic BaseSettings.

Values are provided via environment variables or a .env file.
If not found, default values are used.

Attributes:
    app_name (str): Name of the application.
    jwt_secret_key (str): Secret key used to sign and verify JWT tokens.
    jwt_algorithm (str): Algorithm used for encoding/decoding JWT tokens.
    access_token_expire_minutes (int): Number of minutes before access tokens expire.
    refresh_token_expire_days (int): Number of days before refresh tokens expire.
    database_url (str): Database connection string (e.g. SQLite, PostgreSQL).
"""
class Settings(BaseSettings):
    app_name: str = "defaultappname"
    jwt_secret_key: str = "defaultsecret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    database_url: str = "sqlite:///database.db"
    model_config = SettingsConfigDict(env_file="../.env", extra='ignore')

@lru_cache
def get_settings():
    """
    Returns a cached Settings instance.

    Using lru_cache ensures that the Settings object is only created once
    and reused across the application.
    """
    return Settings()
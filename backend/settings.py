from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "defaultappname"
    jwt_secret_key: str = "defaultsecret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    model_config = SettingsConfigDict(env_file="../.env")

@lru_cache
def get_settings():
    return Settings()
import os

from pydantic_settings import BaseSettings
from pydantic import Field


class Database(BaseSettings):
    postgres_user: str = Field(..., env='POSTGRES_USER')
    postgres_password: str = Field(..., env='POSTGRES_USER')
    postgres_db: str = Field(..., env='POSTGRES_DB')
    postgres_host: str = Field(..., env='POSTGRES_HOST')
    postgres_port: str = Field(..., env='POSTGRES_PORT')

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


class Redis(BaseSettings):
    redis_port: str = "6379"
    redis_password: str = Field(..., env='REDIS_PASSWORD')


class Settings(BaseSettings):
    bot_token: str = Field(..., env='BOT_TOKEN')
    admins: list = Field(..., env='ADMINS')
    timezone: str = "Europe/Madrid"

    db: Database = Database()
    redis: Redis = Redis()

    timezone: str = "Europe/Moscow"
    roles: dict = {
        "mech": "mechanic",
        "admin": "admin",
        "su": "super user"
    }
    languages: dict = {
        "en": "English",
        "ru": "Русский",
        "es": "Español",
    }

    translation_file: str = "translations1.json"


settings = Settings()


from pydantic_settings import BaseSettings
from pydantic import Field

CALENDAR_MONTHS = {
    "ru": {
        1: "Январь",
        2: "Февраль",
        3: "Март",
        4: "Апрель",
        5: "Май",
        6: "Июнь",
        7: "Июль",
        8: "Август",
        9: "Сентябрь",
        10: "Октябрь",
        11: "Ноябрь",
        12: "Декабрь"
    },
    "en": {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December"
    },
    "es": {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre"
    }
}


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
    calendar_months: dict = CALENDAR_MONTHS

    db: Database = Database()
    redis: Redis = Redis()

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


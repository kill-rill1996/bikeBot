import json

from settings import settings
from logger import logger


class Translator:

    def __init__(self):
        self.translation_file = settings.translation_file
        self.translation: dict | None = None

    def _load_translations(self):
        """Загружает переводы из файла в кэш."""

        # Проверяем, нужно ли загружать/перезагружать
        if not self.translation:

            try:
                with open(settings.translation_file, "r", encoding="utf-8") as f:
                    self.translation = json.load(f)
                    logger.info(f"Translations loaded successfully from {settings.translation_file}")

            except FileNotFoundError:
                logger.error(f"Translations file not found: {settings.translation_file}. Using empty cache.")
                self.translation = {}

            except json.JSONDecodeError as e:
                logger.error(f"Error decoding translations file {settings.translation_file}: {e}. Using empty cache.")
                self.translation = {}

            except Exception as e:
                logger.error(f"Unexpected error loading translations: {e}. Using empty cache.")
                self.translation = {}

    def t(self, key: str, dest_lang: str) -> str:
        """Перевод строки в необходимый язык"""
        language_dictionary = self.translation.get(dest_lang, {})
        return language_dictionary.get(key, key)


translator = Translator()
translator._load_translations()

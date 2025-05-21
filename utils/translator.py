import json

from googletrans import Translator as GoogleTrans


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

    async def t(self, key: str, dest_lang: str, text: str | None = None) -> str:
        """
        Перевод строки в необходимый язык
        key: str key phrase to translation dictionary
        text: str | None optional arg for Google translator

        """
        # получаем необходимый словарь
        language_dictionary = self.translation.get(dest_lang, {})

        # по ключу получает необходимый перевод фразы, если фразы нет - None
        translated_phrase = language_dictionary.get(key, None)

        # если фразу не нашло, переводим через гугл
        if not translated_phrase:
            async with GoogleTrans() as google_trans:
                translated = await google_trans.translate(text=text, dest=dest_lang)
                return translated.text

        return translated_phrase


translator = Translator()
translator._load_translations()

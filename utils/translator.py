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

    async def update_translation(self, data: dict) -> None:
        """
        Записывает в переводчик новые слова
        data = {'ru': word, 'en': word, 'es': word}
        """
        # проверяем загружен ли перевод в память, если нет то загружаем
        if not self.translation:
            self._load_translations()

        # добавляем новые переводы слов
        new_key = await self.get_key_for_text(data["en"])
        print(new_key)

        for k, v in data.items():
            self.translation[k][new_key] = v

        # перезаписываем файл
        try:
            with open(settings.translation_file, "w", encoding="utf-8") as f:
                json.dump(self.translation, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Ошибка при перезаписи файла переводов: {e}")
            raise

    @staticmethod
    async def get_key_for_text(text: str) -> str:
        return '_'.join([word.lower() for word in text.split(" ")])

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
                translated = await google_trans.translate(text=key, dest=dest_lang)
                return translated.text

        return translated_phrase


async def neet_to_translate_on(lang: str) -> list[str]:
    """Возвращает лист языков на которые нужно перевести"""
    need_to_translate = []
    for key in settings.languages.keys():
        if key != lang:
            need_to_translate.append(key)

    return need_to_translate


translator = Translator()
translator._load_translations()

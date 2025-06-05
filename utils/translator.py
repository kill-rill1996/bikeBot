import json
import math
from time import time

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

    async def add_new_translation(self, new_data: dict) -> str:
        """
        Записывает в переводчик новые слова и возвращает новый ключ
        data: dict = {'ru': word, 'en': word, 'es': word}
        :return key
        """
        # проверяем загружен ли перевод в память, если нет то загружаем
        if not self.translation:
            self._load_translations()

        # добавляем новые переводы слов
        new_key = await self.get_key_for_text(new_data["en"])

        for k, v in new_data.items():
            self.translation[k][new_key] = v

        # перезаписываем файл
        self._rewrite_dictionary_file()

        return new_key

    async def _key_already_exists(self, key: str) -> bool:
        """Возвращает true, если такой ключ уже существует, иначе false"""
        # проверяем загружен ли перевод в память, если нет то загружаем
        if not self.translation:
            self._load_translations()

        return key in self.translation['en']

    async def delete_key_word(self, keyword: str) -> None:
        """
        Удаляет значения и сам ключ
        :param keyword: str; ключ для поиска переводов
        :return: None
        """
        # проверяем загружен ли перевод в память, если нет то загружаем
        if not self.translation:
            self._load_translations()

        for lang in self.translation.keys():
            try:
                del self.translation[lang][keyword]
            except Exception as e:
                logger.error(f"Ошибка при удалении ключа {keyword}: {e}")
                raise

        # перезаписываем файл
        self._rewrite_dictionary_file()

    def _rewrite_dictionary_file(self):
        """Перезаписывает файл с текущим значением словаря в self.translation"""
        try:
            with open(settings.translation_file, "w", encoding="utf-8") as f:
                json.dump(self.translation, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Ошибка при перезаписи файла переводов: {e}")
            raise

    async def get_key_for_text(self, text: str) -> str:
        # формируем новый ключ
        key_string = '_'.join([word.lower() for word in text.split(" ")])

        # проверяем существует ли такой
        if await self._key_already_exists(key_string):
            key_string += f"_{str(math.modf(time())[0])[4:9]}"  # добавляем к ключу unix time для уникальности

        return key_string

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

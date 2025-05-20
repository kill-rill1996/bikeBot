from utils.translator import translator as t


def get_back_button(callback_url: str, lang: str) -> tuple:
    """Получаем кнопку назад"""
    text = "↩️ " + t.t("back", lang)
    return text, f"{callback_url}"


def get_main_menu_button(lang: str) -> tuple:
    """Кнопка главное меню"""
    text = t.t("main_menu", lang)
    return text, "main-menu"

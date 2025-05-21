from utils.translator import translator as t


async def get_back_button(callback_url: str, lang: str) -> tuple:
    """Получаем кнопку назад"""
    text = "↩️ " + await t.t("back", lang)
    return text, f"{callback_url}"


async def get_main_menu_button(lang: str) -> tuple:
    """Кнопка главное меню"""
    text = await t.t("main_menu", lang)
    return text, "main-menu"

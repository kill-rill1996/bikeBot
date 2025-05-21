from typing import Any

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from routers.states.registration import RegUsersFSM

from database.orm import AsyncOrm

from routers.keyboards import menu as kb

from utils.translator import translator

from settings import settings
from cache import r

router = Router()


@router.message(Command("start"))
@router.callback_query(F.data == "cancel_registration")
async def start_handler(message: types.Message | types.CallbackQuery, session: Any, admin: bool, state: FSMContext) -> None:
    """Обработка команды старт"""
    tg_id = str(message.from_user.id)

    # проверяем существует ли пользователь в БД
    user_exists: bool = await AsyncOrm.check_user_already_exists(tg_id, session)

    # если нет, регистрируем его (Имя, язык)
    if not user_exists:
        # start FSM
        await state.set_state(RegUsersFSM.lang)
        text = "Выберите язык / Choose language / Elija idioma:"

        if type(message) == types.Message:
            await message.answer(text, reply_markup=kb.pick_language().as_markup())
        else:
            await message.message.edit_text(text, reply_markup=kb.pick_language().as_markup())

    else:
        user_lang = r.get(f"lang:{tg_id}")

        if not user_lang:
            user_lang = await AsyncOrm.get_user_language(session, tg_id)
            # добавляем язык для пользователя в кэш
            r.set(f"lang:{tg_id}", user_lang)
        else:
            user_lang = user_lang.decode()

        # переводим пользователя на главное меню
        text = await translator.t("main_menu", user_lang)

        keyboard = await kb.main_menu_keyboard(admin, user_lang)
        await message.answer(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("_")[0] == "lang", RegUsersFSM.lang)
async def set_username(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Запрос username от пользователя"""
    # записываем язык
    lang = callback.data.split("_")[1]
    await state.update_data(lang=lang)

    # меняем state
    await state.set_state(RegUsersFSM.username)

    text = await translator.t("input_name", lang)

    keyboard = await kb.cancel_registration(lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.message(RegUsersFSM.username)
async def get_username_from_text(message: types.Message, state: FSMContext, session: Any, admin: bool) -> None:
    """Запись имени"""
    name = message.text
    data = await state.get_data()
    lang = data["lang"]

    # при пустом имени
    if name == "":
        text = await translator.t("name_error", lang)
        await message.answer(text)
        return

    tg_id = str(message.from_user.id)
    tg_username = message.from_user.username

    # очищаем state
    await state.clear()

    await AsyncOrm.create_user(
        session,
        tg_id=tg_id,
        tg_username=tg_username,
        username=name,
        role=settings.roles["mech"],
        lang=lang
    )

    text = await translator.t("success_creation", lang).format(name, settings.languages[lang])
    await message.answer(text)

    # переводим в главное меню
    text = await translator.t("main_menu", lang)

    keyboard = await kb.main_menu_keyboard(admin, lang)
    await message.answer(text, reply_markup=keyboard.as_markup())

    # добавляем язык для пользователя в кэш
    r.set(f"lang:{tg_id}", lang)


@router.message(Command("test"))
async def test_translator(message: types.Message) -> None:
    result = await translator.t(key="pencil", dest_lang="es", text="🔄 ыдвлаьыдвьалуьд")
    await message.answer(result)







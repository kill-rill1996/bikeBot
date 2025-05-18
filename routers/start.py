from typing import Any

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from routers.states.registration import RegUsersFSM

from database.orm import AsyncOrm

from routers.keyboards import menu as kb

from utils.translator import translator

from settings import settings

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message, session: Any, admin: bool, state: FSMContext) -> None:
    """Обработка команды старт"""
    tg_id = str(message.from_user.id)

    # проверяем существует ли пользователь в БД
    user_exists: bool = await AsyncOrm.check_user_already_exists(tg_id, session)

    # если нет, регистрируем его (Имя, язык)
    if not user_exists:
        # start FSM
        await state.set_state(RegUsersFSM.lang)
        await message.answer("Выберите язык / Choose language / Elija idioma:", reply_markup=kb.pick_language().as_markup())

    else:
        user = await AsyncOrm.get_user(session)
        # переводим пользователя на главное меню
        translator.t("Главное меню")
        await message.answer("Главное меню", reply_markup=kb.main_menu_keyboard(admin).as_markup())


@router.callback_query(F.data.split("_")[0] == "lang", RegUsersFSM.lang)
async def set_username(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Запрос username от пользователя"""
    # записываем язык
    lang = callback.data.split("_")[1]
    await state.update_data(lang=lang)

    # меняем state
    await state.set_state(RegUsersFSM.username)

    # TODO уже делать на нужном языке
    await callback.message.edit_text("Input username (ex. Pasha Biceps)")


@router.message(RegUsersFSM.username)
async def get_username_from_text(message: types.Message, state: FSMContext, session: Any, admin: bool) -> None:
    """Запись имени"""
    name = message.text

    # при пустом имени
    if name == "":
        await message.answer("Имя пользователя не может быть пустым, введите еще раз")
        return

    tg_id = str(message.from_user.id)
    tg_username = message.from_user.username
    data = await state.get_data()

    # очищаем state
    await state.clear()

    await AsyncOrm.create_user(
        session,
        tg_id=tg_id,
        tg_username=tg_username,
        username=name,
        role=settings.roles["mech"],
        lang=data["lang"]
    )

    await message.answer("Ваш профиль успешно создан\n<i>Вы всегда можете изменить имя и язык в ⚙️ Настройках</i>")
    # переводим в главное меню
    await message.answer("Главное меню", reply_markup=kb.main_menu_keyboard(admin).as_markup())









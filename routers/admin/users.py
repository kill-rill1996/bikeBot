from typing import Any

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from database.orm import AsyncOrm
from routers.keyboards import users as kb
from routers.states.users import AddUserFSM
from utils.translator import translator as t
from cache import r
from utils.validations import is_valid_tg_id
from utils.date_time_service import convert_date_time

router = Router()


@router.callback_query(F.data == "admin|user_management")
async def users_menu(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Меню управления пользователями"""
    try:
        await state.clear()
    except Exception:
        pass

    lang = r.get(f"lang:{tg_id}").decode()

    text = f"👤 {await t.t('user_management', lang)}"

    keyboard = await kb.users_menu_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "add_user")
async def add_user_start(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Начало добавления пользователя"""
    lang = r.get(f"lang:{tg_id}").decode()

    text = await t.t('insert_tg_id', lang)

    await state.set_state(AddUserFSM.tg_id)

    keyboard = await kb.cancel_keyboard(lang)
    msg = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_mess=msg)


@router.message(AddUserFSM.tg_id)
async def get_user_tg_id(message: types.Message, tg_id: str, state: FSMContext) -> None:
    """Запись tg_id"""
    # изменение предыдущего сообщения
    data = await state.get_data()
    try:
        await data["prev_mess"].edit_text(data["prev_mess"].text)
    except Exception:
        pass

    lang = r.get(f"lang:{tg_id}").decode()

    user_tg_id = message.text

    # если некорректное число
    if not is_valid_tg_id(user_tg_id):
        text = await t.t("must_be_integer", lang)
        keyboard = await kb.cancel_keyboard(lang)
        msg = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_mess=msg)
        return

    await state.update_data(user_tg_id=user_tg_id)
    await state.set_state(AddUserFSM.username)

    text = await t.t("send_username", lang)
    keyboard = await kb.cancel_keyboard(lang)
    msg = await message.answer(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_mess=msg)


@router.message(AddUserFSM.username)
async def get_user_username(message: types.Message, tg_id: str, state: FSMContext) -> None:
    """Запись username"""
    # изменение предыдущего сообщения
    data = await state.get_data()
    try:
        await data["prev_mess"].edit_text(data["prev_mess"].text)
    except Exception:
        pass

    lang = r.get(f"lang:{tg_id}").decode()

    username = message.text

    await state.update_data(username=username)
    await state.set_state(AddUserFSM.role)

    text = await t.t('send_role', lang)
    keyboard = await kb.choose_user_role(lang)
    await message.answer(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "role", AddUserFSM.role)
async def get_role(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Запись роли"""
    lang = r.get(f"lang:{tg_id}").decode()
    role = callback.data.split("|")[1]

    data = await state.get_data()

    await state.update_data(role=role)
    await state.set_state(AddUserFSM.confirmation)

    text = await t.t("add_user_confirm", lang)
    keyboard = await kb.confirm_keyboard(lang)
    await callback.message.edit_text(text.format(await t.t(role, lang), data["username"]), reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "add_user_confirmed", AddUserFSM.confirmation)
async def add_user_confirmed(callback: types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """Запись роли"""
    lang = r.get(f"lang:{tg_id}").decode()

    data = await state.get_data()
    await state.clear()

    # добавляем в таблицу User
    await AsyncOrm.create_user(session, data["user_tg_id"], None, data["username"], data["role"], "en")
    # добавляем в таблицу AllowedUser
    await AsyncOrm.create_allow_user(data["user_tg_id"], session)

    text = await t.t("user_added", lang)
    keyboard = await kb.back_and_main_menu(lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "show_user")
async def add_user_start(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Просмотр пользователей"""
    lang = r.get(f"lang:{tg_id}").decode()

    users = await AsyncOrm.get_all_users(session)

    text = await t.t("choose_user", lang)
    keyboard = await kb.users_keyboard(users, lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "show_user_choose")
async def user_details(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Просмотр пользователя"""
    lang = r.get(f"lang:{tg_id}").decode()
    user_id = int(callback.data.split("|")[1])

    user = await AsyncOrm.get_user_by_id(user_id, session)

    text = f"{user.tg_id} | {user.username} | {user.role} | {convert_date_time(user.created_at, with_tz=True)[0]}"
    keyboard = await kb.user_detail_keyboard(user, lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "edit_user")
async def edit_user(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Редактирование пользователя"""
    lang = r.get(f"lang:{tg_id}").decode()
    user_id = int(callback.data.split("|")[1])
    pass


@router.callback_query(F.data.split("|")[0] == "delete_user")
async def delete_user(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Запрос удаления пользователя"""
    lang = r.get(f"lang:{tg_id}").decode()
    user_id = int(callback.data.split("|")[1])

    user = await AsyncOrm.get_user_by_id(user_id, session)

    text = await t.t("delete_user_confirm", lang)
    keyboard = await kb.delete_confirm_keyboard(user.id, lang)
    await callback.message.edit_text(text.format(await t.t(user.role, lang), user.username), reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "delete_user_confirmed")
async def delete_user(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Удаление пользователя"""
    lang = r.get(f"lang:{tg_id}").decode()
    user_id = int(callback.data.split("|")[1])
    user = await AsyncOrm.get_user_by_id(user_id, session)

    await AsyncOrm.delete_user(user.tg_id, session)

    text = await t.t("user_deleted", lang)
    keyboard = await kb.back_and_main_menu(lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())







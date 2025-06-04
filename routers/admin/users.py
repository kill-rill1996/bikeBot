from typing import Any

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from database.orm import AsyncOrm
from routers.keyboards import users as kb
from routers.states.users import AddUserFSM, EditUsernameFSM, EditRoleFSM
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
async def get_user_tg_id(message: types.Message, tg_id: str, state: FSMContext, session: Any) -> None:
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

    # если такой пользователь уже есть
    users_tg_ids = await AsyncOrm.get_allowed_users_tg_ids(session)
    if user_tg_id in users_tg_ids:
        text = await t.t("user_already_exists", lang)
        keyboard = await kb.cancel_keyboard(lang)
        msg = await message.answer(text.format(user_tg_id), reply_markup=keyboard.as_markup())
        await state.update_data(prev_mess=msg)
        return

    await state.update_data(user_tg_id=user_tg_id)
    await state.set_state(AddUserFSM.confirmation)

    text = await t.t("add_user_confirm", lang)
    keyboard = await kb.confirm_keyboard(lang)
    await message.answer(text.format(user_tg_id), reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "add_user_confirmed", AddUserFSM.confirmation)
async def add_user_confirmed(callback: types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """Запись роли"""
    lang = r.get(f"lang:{tg_id}").decode()

    data = await state.get_data()
    await state.clear()

    # добавляем в таблицу AllowedUser
    await AsyncOrm.create_allow_user(data["user_tg_id"], session)

    # добавляем в кэш
    r.set(f"allowed_users:{data['user_tg_id']}", "allowed")

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

    text = f"{user.tg_id} | {user.username} | {await t.t(user.role, lang)} | {convert_date_time(user.created_at, with_tz=True)[0]}"
    keyboard = await kb.user_detail_keyboard(user, lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "edit_user")
async def edit_user(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Редактирование пользователя"""
    try:
        await state.clear()
    except Exception:
        pass

    lang = r.get(f"lang:{tg_id}").decode()
    user_id = int(callback.data.split("|")[1])

    user = await AsyncOrm.get_user_by_id(user_id, session)

    text = await t.t("edit_user", lang) + "\n" + f"{await t.t(user.role, lang)} {user.username}"
    keyboard = await kb.choose_param_edit_user(user_id, lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "edit_username")
async def edit_username_start(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Начало редактирования имени пользователя"""
    lang = r.get(f"lang:{tg_id}").decode()
    user_id = int(callback.data.split("|")[1])

    await state.set_state(EditUsernameFSM.username)
    await state.update_data(user_id=user_id)

    text = await t.t("send_username", lang)
    keyboard = await kb.cancel_edit_keyboard(user_id, lang)
    msg = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_mess=msg)


@router.message(EditUsernameFSM.username)
async def get_username_for_edit(message: types.Message, tg_id: str, state: FSMContext, session: Any) -> None:
    """Получение нового имени пользователя"""
    lang = r.get(f"lang:{tg_id}").decode()
    username = message.text
    await state.update_data(username=username)

    # меняем предыдущее сообщение
    data = await state.get_data()
    try:
        await data["prev_mess"].edit_text(data["prev_mess"].text)
    except Exception:
        pass

    data = await state.get_data()
    user = await AsyncOrm.get_user_by_id(data["user_id"], session)
    await state.set_state(EditUsernameFSM.confirmation)

    text = await t.t("edit_username_confirm", lang)
    keyboard = await kb.edit_user_param_confirm(user.id, lang)
    await message.answer(text.format(user.username, username), reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "edit_role")
async def edit_role_start(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Начало редактирования роли пользователя"""
    lang = r.get(f"lang:{tg_id}").decode()
    user_id = int(callback.data.split("|")[1])

    await state.set_state(EditRoleFSM.role)
    await state.update_data(user_id=user_id)

    text = await t.t("send_role", lang)
    keyboard = await kb.choose_user_role_for_edit(user_id, lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "new_role", EditRoleFSM.role)
async def get_role_for_edit(callback: types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """Запись новой роли пользователя"""
    lang = r.get(f"lang:{tg_id}").decode()
    user_id = int(callback.data.split("|")[1])
    role = callback.data.split("|")[2]

    await state.update_data(role=role)
    await state.set_state(EditRoleFSM.confirmation)

    user = await AsyncOrm.get_user_by_id(user_id, session)

    text = await t.t("edit_role_confirm", lang)
    formatted_text = text.format(user.username, await t.t(user.role, lang), await t.t(role, lang))

    keyboard = await kb.edit_user_param_confirm(user_id, lang)

    await callback.message.edit_text(formatted_text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "edit_user_confirmed", EditUsernameFSM.confirmation)
@router.callback_query(F.data.split("|")[0] == "edit_user_confirmed", EditRoleFSM.confirmation)
async def edit_user_param_end(callback: types.CallbackQuery, tg_id: int, state: FSMContext, session: Any) -> None:
    """Изменение параметров пользователя"""
    lang = r.get(f"lang:{tg_id}").decode()
    user_id = int(callback.data.split("|")[1])

    data = await state.get_data()

    # редактируем имя
    if data.get("username"):
        await AsyncOrm.edit_username(user_id, data["username"], session)

    # редактируем роль
    else:
        await AsyncOrm.edit_role(user_id, data["role"], session)

        # заменяем кэш с админами
        db_admins = await AsyncOrm.get_admins(session)
        db_admins_str = "|".join(db_admins)
        r.delete("admins")
        r.set("admins", db_admins_str)

    # очищаем стейт
    await state.clear()

    text = await t.t("user_edited", lang)
    keyboard = await kb.user_edited(user_id, lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


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

    # удаление из БД
    await AsyncOrm.delete_user(user.tg_id, session)

    # удаление из кэша
    r.delete(f"allowed_users:{user.tg_id}")

    text = await t.t("user_deleted", lang)
    keyboard = await kb.back_and_main_menu(lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())







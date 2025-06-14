from typing import Any

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from database.orm import AsyncOrm
from routers.keyboards import delete_work as kb
from routers.states.delete_work import DeleteWorkFSM
from routers.states.locations import AddLocationFSM, EditLocationFSM
from schemas.location import Location
from utils.date_time_service import convert_date_time
from utils.translator import translator as t, neet_to_translate_on
from cache import r
from utils.validations import is_valid_operation_id

router = Router()

CONFIRM_MESSAGE = "Admin123"


@router.callback_query(F.data == "admin|delete_work")
async def delete_work_start(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Ввод id работы"""
    lang = r.get(f"lang:{tg_id}").decode()

    await state.set_state(DeleteWorkFSM.operation_id)

    text = f"{await t.t('send_work_number', lang)}"

    keyboard = await kb.send_work_id_keyboard(lang)
    msg = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_mess=msg)


@router.message(DeleteWorkFSM.operation_id)
async def get_work_id(message: types.Message, tg_id: str, state: FSMContext, session: Any) -> None:
    """Получение operation_id"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()
    operation_id = message.text

    # меняем предыдущее сообщение
    try:
        await data["prev_mess"].edit_text(data["prev_mess"].text)
    except Exception:
        pass

    # получение всех id операций
    operations_ids = await AsyncOrm.get_operations_ids(session)

    # неправильный номер
    if not is_valid_operation_id(operation_id, operations_ids):
        # отправляем сообщение об ошибке
        text = await t.t("wrong_operation_id", lang)
        keyboard = await kb.send_work_id_keyboard(lang)
        msg = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_mess=msg)
        return

    # правильный номер
    else:
        # меняем стейт
        await state.set_state(DeleteWorkFSM.password)

        # записываем operation_id
        await state.update_data(operation_id=int(operation_id))

        operation = await AsyncOrm.get_operation_by_id(int(operation_id), session)

        # формируем текст
        date, time = convert_date_time(operation.created_at, with_tz=True)
        text = f"ID {operation.id} | {date} {time} | {str(operation.duration)} {await t.t('minutes', lang)} | " \
                   f"{await t.t(operation.transport_category, lang)} {operation.transport_subcategory}-{operation.transport_serial_number}\n"

        # группа узлов
        text += await t.t(operation.jobs[0].jobtype_title, lang) + ":\n"

        # jobs для каждой операции
        for job in operation.jobs:
            text += "\t\t• " + await t.t(job.title, lang) + "\n"

        # комментарий
        comment = operation.comment if operation.comment else "-"
        text += f'{await t.t("comment", lang)} <i>"{comment}"</i>\n'

        keyboard = await kb.delete_operation_keyboard(lang)
        await message.answer(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "delete_operation", DeleteWorkFSM.password)
async def password_for_delete(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Запрос пароля для удаления"""
    lang = r.get(f"lang:{tg_id}").decode()

    await state.set_state(DeleteWorkFSM.confirmation)

    text = f"{await t.t('send_password', lang)}"

    keyboard = await kb.back_to_operation(lang)
    msg = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_mess=msg)


@router.message(DeleteWorkFSM.confirmation)
async def confirmation_delete(message: types.Message, tg_id: str, state: FSMContext, session: Any) -> None:
    """Проверка пароля и запрос подтверждения"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()
    password = message.text

    # меняем предыдущее сообщение
    try:
        await data["prev_mess"].edit_text(data["prev_mess"].text)
    except Exception:
        pass

    # если неправильный пароль
    if password != CONFIRM_MESSAGE:
        # отправляем сообщение об ошибке
        text = await t.t("wrong_password", lang)
        keyboard = await kb.back_to_operation(lang)
        msg = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_mess=msg)
        return

    # если правильный пароль
    else:
        await state.set_state(DeleteWorkFSM.second_confirmation)

        text = await t.t("confirm_delete_work", lang)
        keyboard = await kb.confirm_delete_keyboard(lang)
        await message.answer(text.format(data["operation_id"]), reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "delete_work_confirmed", DeleteWorkFSM.second_confirmation)
async def delete_work(callback: types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """Удаление работы"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()
    operation_id = data["operation_id"]

    # удаление из БД
    await AsyncOrm.delete_operation(operation_id, session)

    # очищаем стейт
    await state.clear()

    text = await t.t("work_deleted", lang)
    keyboard = await kb.work_deleted_keyboard(lang)
    await callback.message.edit_text(text.format(operation_id), reply_markup=keyboard.as_markup())

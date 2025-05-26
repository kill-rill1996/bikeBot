import datetime
from typing import Any

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from cache import r
from utils.translator import translator as t
from utils.date_time_service import convert_date_time

from routers.keyboards.works import works_menu_keyboard
from routers.keyboards import my_works as kb
from routers.messages import my_works as ms
from routers.states.edit_work import EditWorkFSM

from schemas.operations import OperationJobs, OperationDetailJobs

from database.orm import AsyncOrm

router = Router()


@router.callback_query(F.data.split("|")[1] == "works-records")
async def works_reports_menu(callback: types.CallbackQuery) -> None:
    """Меню учета выполненных работ"""
    tg_id = str(callback.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()

    text = "📋 " + await t.t("work_records", lang)

    keyboard = await works_menu_keyboard(lang)
    await callback.message.edit_text(text=text, reply_markup=keyboard.as_markup())


# MY WORKS
@router.callback_query(F.data.split("|")[1] == "my-works")
async def my_works_period(callback: types.CallbackQuery, tg_id: str) -> None:
    """Мои работы выбор периода"""
    lang = r.get(f"lang:{tg_id}").decode()

    text = await t.t("select_period", lang)
    keyboard = await kb.works_period_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "my-works")
async def my_works_list(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Вывод списка работ за выбранный период"""
    lang = r.get(f"lang:{tg_id}").decode()

    # получаем выбранный период и формируем start/end период выборки
    period = callback.data.split("|")[1]

    if period == "today":
        start_period = datetime.datetime.now().date()   # делаем только дату без времени
        end_period = datetime.datetime.now()

    elif period == "yesterday":
        start_period = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
        end_period = datetime.datetime.strptime(start_period.strftime("%Y-%m-%d") + " 23:59:59", "%Y-%m-%d %H:%M:%S")

    elif period == "week":
        end_period = datetime.datetime.now()
        start_period = end_period - datetime.timedelta(days=7)

    elif period == "month":
        end_period = datetime.datetime.now()
        start_period = end_period - datetime.timedelta(days=30)  # ставим для месяца 30 дней

    else:
        # TODO заглушка
        end_period = datetime.datetime.now()
        start_period = datetime.datetime.now()
        await callback.message.edit_text("Введите кастомный период")
        return

    # получаем operations с их jobs
    # TODO add cache
    operations: list[OperationJobs] = await AsyncOrm.select_operations(start_period, end_period, tg_id, session)

    # формируем клавиатуру
    keyboard = await kb.works_my_works_list(lang, operations, period)

    # если еще нет работ
    if not operations:
        text = await t.t("empty_works", lang)
        await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
        return

    text = await t.t("works_list", lang)

    # TODO пагинация
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "my-works-list")
async def work_detail(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Вывод подробного описания работы"""
    lang = r.get(f"lang:{tg_id}").decode()
    # период получаем из колбэка (чтобы потом можно было кнопку назад сделать)
    period = callback.data.split("|")[2]

    operation_id = int(callback.data.split("|")[1])

    # TODO add cache
    operation: OperationDetailJobs = await AsyncOrm.select_operation(operation_id, session)

    message = await ms.work_detail_message(lang, operation)
    keyboard = await kb.work_details(lang, operation_id, period)

    await callback.message.edit_text(message, reply_markup=keyboard.as_markup())


# UPDATE WORK
@router.callback_query(F.data.split("|")[0] == "edit-work")
async def edit_my_work(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Изменение работы"""
    # скидываем state (для случаев когда пришли с кнопки назад)
    try:
        await state.clear()
    except:
        pass

    lang = r.get(f"lang:{tg_id}").decode()
    # получаем данные для формирования кнопок "назад"
    operation_id = int(callback.data.split("|")[1])
    period = callback.data.split("|")[2]

    # получаем работу
    operation: OperationDetailJobs = await AsyncOrm.select_operation(operation_id, session)

    # проверяем когда была создана работа, если больше чем 24 часа, то запрещаем изменение
    if operation.created_at < datetime.datetime.now() - datetime.timedelta(hours=24):
        text = await t.t("work_24", lang)
        keyboard = await kb.back_keyboard(lang, period, operation_id)
        await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
        return

    # начинаем FSM изменения комментария
    await state.set_state(EditWorkFSM.enter_comment)
    await state.update_data(period=period)
    await state.update_data(operation_id=operation_id)

    # если еще можно изменить работу
    text = await t.t("your_comment", lang) + "\n\n" + f"<i>{operation.comment}</i>" + "\n\n" \
           + await t.t("enter_new_comment", lang)
    keyboard = await kb.back_keyboard(lang, period, operation_id)

    prev_mess = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_mess=prev_mess)


@router.message(EditWorkFSM.enter_comment)
async def editing_comment(message: types.Message, state: FSMContext, tg_id: str) -> None:
    """Получаем новый комментарий из текста """
    lang = r.get(f"lang:{tg_id}").decode()

    # получаем комментарий из отправленного текста
    try:
        new_comment = str(message.text)
    except:
        await message.answer("Wrong comment, try again")
        return

    # меняем state
    await state.set_state(EditWorkFSM.confirm)
    # сохраняем комментарий в data
    await state.update_data(new_comment=new_comment)

    # получаем данные для колбэков
    data = await state.get_data()

    # удаляем пред. сообщение
    try:
        await data["prev_mess"].delete()
    except Exception:
        pass

    text = await t.t("your_new_comment", lang) + f"\n\n<i>{new_comment}</i>"
    keyboard = await kb.confirm_edit_comment_keyboard(lang, data["operation_id"], data["period"])
    await message.answer(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "save-changes-comment", EditWorkFSM.confirm)
async def save_new_comment(callback: types.CallbackQuery, state: FSMContext, tg_id: str, session: Any) -> None:
    """Сохранение нового комментария и конец FSM"""
    lang = r.get(f"lang:{tg_id}").decode()

    # получаем данные
    data = await state.get_data()
    # очищаем state
    await state.clear()

    # отправляем сообщение об ожидании
    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))

    # изменяем в БД
    await AsyncOrm.update_comment(data["operation_id"], data["new_comment"], session)

    await state.clear()

    text = await t.t("comment_saved", lang)
    keyboard = await kb.after_comment_updated_keyboard(lang)
    await waiting_message.edit_text(text, reply_markup=keyboard.as_markup())


# DELETE WORK
@router.callback_query(F.data.split("|")[0] == "delete-work")
async def delete_my_work(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Удаление работы"""
    lang = r.get(f"lang:{tg_id}").decode()
    operation_id = int(callback.data.split("|")[1])
    period = callback.data.split("|")[2]

    operation: OperationDetailJobs = await AsyncOrm.select_operation(operation_id, session)

    # формируем текст с данными из перевода
    created_at = convert_date_time(operation.created_at, True)[0]
    transport_category = await t.t(operation.transport_category, lang)
    job_title = await t.t(operation.job_title, lang)
    text = f"{created_at}|{operation.id}|{transport_category}|{operation.transport_subcategory}-{operation.serial_number}|{job_title}"

    # добавляем вопрос об удалении
    text += "\n\n" + f"<b>{await t.t('sure_delete', lang)}</b>"
    keyboard = await kb.delete_work(lang, operation_id, period)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "delete-work-confirm")
async def delete_my_work(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Удаление работы"""
    lang = r.get(f"lang:{tg_id}").decode()
    operation_id = int(callback.data.split("|")[1])

    # защита от ошибки при удалении из БД
    try:
        await AsyncOrm.delete_work(operation_id, session)
    except:
        await callback.message.edit_text("Error while deleting, try again later...")
        return

    # успешное удаление
    text = await t.t("success_delete", lang)
    keyboard = await kb.after_comment_updated_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


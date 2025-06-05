from typing import Any

from aiogram import Router, F, types
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext

from cache import r
from routers.states.jobs import AddJobtype, EditJobetype, AddJob, EditJob
from schemas.categories_and_jobs import Category, Jobtype
from utils.translator import translator as t, neet_to_translate_on
from database.orm import AsyncOrm
from routers.keyboards import jobs as kb

router = Router()


# JOBS management menu
@router.callback_query(F.data == "admin|operation_management")
async def jobs_menu(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Меню управления операциями"""
    lang = r.get(f"lang:{tg_id}").decode()

    # Скидывем state
    try:
        await state.clear()
    except Exception:
        pass

    text = f"🛠 {await t.t('operation_management', lang)}"

    keyboard = await kb.jobs_management_menu_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


# ADD / EDIT JOB_TYPE
@router.callback_query(or_f(F.data == "jobs-management|add_jobtype", F.data == "jobs-management|edit_jobtype"))
async def add_jobtype(callback: types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """Получаем тип операции"""
    lang = r.get(f"lang:{tg_id}").decode()

    # FOR ADD
    if callback.data == "jobs-management|add_jobtype":
        await state.set_state(AddJobtype.input_jobtype)
        text = await t.t("input_jobtype", lang)
        keyboard = await kb.back_keyboard(lang, "admin|operation_management")

        prev_message = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)

    # FOR EDIT
    else:
        await state.set_state(EditJobetype.input_jobtype)
        all_jobtypes: list[Jobtype] = await AsyncOrm.get_all_jobtypes(session)
        text = await t.t("select_jobtype", lang)
        keyboard = await kb.jobetypes_keyboard(all_jobtypes, lang)
        await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


# FOR EDIT
@router.callback_query(EditJobetype.input_jobtype)
@router.callback_query(F.data.split("|")[0] == "back-to-select-type-from-multi", EditJobetype.select_categories)
async def get_jobtype(callback: types.CallbackQuery, tg_id, state: FSMContext, session: Any) -> None:
    """Для изменения получаем тип который мы будем менять"""
    lang = r.get(f"lang:{tg_id}").decode()
    jobtype_id = int(callback.data.split("|")[1])

    await state.set_state(EditJobetype.input_new_jobtype_title)

    jobtype: Jobtype = await AsyncOrm.get_jobtype_by_id(jobtype_id, session)
    await state.update_data(jobtype_id=jobtype.id)

    text = f"\"{jobtype.emoji + ' ' if jobtype.emoji else ''} {await t.t(jobtype.title, lang)}\"\n\n"
    text += await t.t("input_new_jobtype", lang)
    keyboard = await kb.back_keyboard(lang, "jobs-management|edit_jobtype")

    prev_message = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_message=prev_message)


@router.message(or_f(AddJobtype.input_jobtype, EditJobetype.input_new_jobtype_title))
@router.callback_query(F.data == "back-from-translate_1")
async def get_jobtype(message: types.Message | types.CallbackQuery, tg_id, state: FSMContext, session: Any) -> None:
    """Получение типа"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()
    current_state = await state.get_state()

    # for Message:
    if type(message) == types.Message:
        try:
            await data["prev_message"].delete()
        except:
            pass
        # неверный формат
        if type(message) != types.Message:
            text = await t.t("wrong_text_data", lang)
            error_keyboard = await kb.back_keyboard(lang, "jobs-management|add_jobtype")
            prev_message = await message.answer(text, reply_markup=error_keyboard.as_markup())
            await state.update_data(prev_message=prev_message)
            return

        text_from_message = message.text

    # from DB
    categories: [Category] = await AsyncOrm.get_all_categories(session)

    # FOR ADD
    if current_state in (AddJobtype.input_jobtype, AddJobtype.translate_1):
        await state.set_state(AddJobtype.select_categories)
        # for multiselect
        selected_categories = []
        await state.update_data(selected_categories=selected_categories)
        error_keyboard = await kb.categories_keyboard(categories, selected_categories, lang,
                                                callback="jobs-management|add_jobtype")

    # FOR EDIT
    elif current_state in (EditJobetype.input_new_jobtype_title, EditJobetype.translate_1):
        await state.set_state(EditJobetype.select_categories)
        # выбираем уже выбранные категории
        jobtype_id: int = data["jobtype_id"]
        selected_categories = await AsyncOrm.get_categories_ids_by_jobtype_id(jobtype_id, session)
        await state.update_data(selected_categories=selected_categories)
        error_keyboard = await kb.categories_keyboard(categories, selected_categories, lang,
                                                callback=f"back-to-select-type-from-multi|{jobtype_id}")

    if type(message) == types.Message:
        await state.update_data(jobtype_title=text_from_message)

    # for multiselect
    await state.update_data(categories_for_select=categories)

    text = await t.t("for_which_transport", lang)

    if type(message) == types.Message:
        await message.answer(text, reply_markup=error_keyboard.as_markup())
    else:
        await message.message.edit_text(text, reply_markup=error_keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "add-jobtype-select", AddJobtype.select_categories)
@router.callback_query(F.data.split("|")[0] == "add-jobtype-select", EditJobetype.select_categories)
async def multiselect_categories(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Мультиселект категорий"""
    lang = r.get(f"lang:{tg_id}").decode()
    category_id = int(callback.data.split("|")[1])
    current_state = await state.get_state()

    # добавляем или удаляем категорию из списка
    data = await state.get_data()
    selected_categories = data["selected_categories"]
    categories_for_select = data["categories_for_select"]

    # удаляем если уже есть
    if category_id in selected_categories:
        selected_categories.remove(category_id)
    # добавляем если нет
    else:
        selected_categories.append(category_id)

    await state.update_data(selected_categories=selected_categories)

    text = await t.t("for_which_transport", lang)

    if current_state == AddJobtype.select_categories:
        keyboard = await kb.categories_keyboard(categories_for_select, selected_categories, lang, callback="jobs-management|add_jobtype")
    else:
        jobtype_id = data["jobtype_id"]
        keyboard = await kb.categories_keyboard(categories_for_select, selected_categories, lang, callback=f"back-to-select-type-from-multi|{jobtype_id}")

    prev_message = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_message=prev_message)


@router.callback_query(F.data == "select_categories_done", AddJobtype.select_categories)
@router.callback_query(F.data == "select_categories_done", EditJobetype.select_categories)
@router.callback_query(F.data == "back-from-translate_2", AddJobtype.translate_2)
@router.callback_query(F.data == "back-from-translate_2", EditJobetype.translate_2)
async def get_translate_1(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()
    current_state = await state.get_state()

    # FOR ADD
    if current_state in (AddJobtype.select_categories, AddJobtype.translate_2):
        await state.set_state(AddJobtype.translate_1)
    # FOR EDIT
    elif current_state in (EditJobetype.select_categories, EditJobetype.translate_2):
        await state.set_state(EditJobetype.translate_1)

    # получаем языки на которые нужно перевести
    languages: list[str] = await neet_to_translate_on(lang)

    # сохраняем требуемые языки в data
    await state.update_data(languages_1=languages[0])
    await state.update_data(languages_2=languages[1])

    keyboard = await kb.back_keyboard(lang, "back-from-translate_1")
    text = await t.t("add_translate", lang) + " " + await t.t(languages[0], lang)

    prev_message = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_message=prev_message)


@router.message(or_f(AddJobtype.translate_1, EditJobetype.translate_1))
@router.callback_query(F.data == "back-from-confirm", AddJobtype.confirm)
@router.callback_query(F.data == "back-from-confirm", EditJobetype.confirm)
async def get_translate_1(message: types.Message | types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Получение первого перевода"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()
    current_state = await state.get_state()

    languages_2 = data["languages_2"]

    # MESSAGE
    if type(message) == types.Message:
        try:
            await data["prev_message"].delete()
        except:
            pass

        text_from_message = message.text
        await state.update_data(translation_1=text_from_message)

    # FOR ADD
    if current_state in (AddJobtype.translate_1, AddJobtype.translate_2, AddJobtype.confirm):
        await state.set_state(AddJobtype.translate_2)
    # FOR EDIT
    else:
        await state.set_state(EditJobetype.translate_2)

    keyboard = await kb.back_keyboard(lang, "back-from-translate_2")
    text = await t.t("add_translate", lang) + " " + await t.t(languages_2, lang)

    if type(message) == types.Message:
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
    else:
        prev_message = await message.message.edit_text(text, reply_markup=keyboard.as_markup())

    await state.update_data(prev_message=prev_message)


@router.message(or_f(AddJobtype.translate_2, EditJobetype.translate_2))
async def get_translate_2(message: types.Message, tg_id: str, state: FSMContext, session: Any) -> None:
    """Получение второго перевода"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()
    current_state = await state.get_state()

    jobtype_title = data["jobtype_title"]
    selected_categories = data["selected_categories"]

    try:
        await data["prev_message"].delete()
    except:
        pass

    text_from_message = message.text
    await state.update_data(translation_2=text_from_message)

    # refresh data
    data = await state.get_data()

    # FOR ADD
    if current_state in (AddJobtype.translate_2, AddJobtype.confirm):
        await state.set_state(AddJobtype.confirm)
        text = await t.t("confirm_jobtype_create", lang) + "\n"
    # FOR EDIT
    else:
        await state.set_state(EditJobetype.confirm)

        jobtype: Jobtype = await AsyncOrm.get_jobtype_by_id(data["jobtype_id"], session)
        # записываем старое значение для того, чтобы удалить потом в словаре
        await state.update_data(old_jobtype=jobtype)

        text = await t.t("confirm_jobtype_update", lang) + "\n" \
               + f"\"{jobtype.emoji + ' ' if jobtype.emoji else ''}{await t.t(jobtype.title, lang)}\" -> "

    categories_show = []
    # get all categories from DB
    categories = await AsyncOrm.get_all_categories(session)
    # выбираем только нужные
    for category in categories:
        if category.id in selected_categories:
            categories_show.append(category)

    text += f"\"{jobtype_title}\"" + "\nдля категорий: "
    for category in categories_show:
        text += f"{category.emoji + ' ' if category.emoji else ''}{await t.t(category.title, lang)}, "
    # убираем последнюю ", "
    text = text[:-2]
    text += "\n\n"

    # добавляем переводы
    text += f"{await t.t(data['languages_1'], lang)}: \"{data['translation_1']}\"\n"
    text += f"{await t.t(data['languages_2'], lang)}: \"{data['translation_2']}\"\n"

    keyboard = await kb.confirm_keyboard(lang)

    prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_message=prev_message)


@router.callback_query(or_f(AddJobtype.confirm, EditJobetype.confirm))
async def confirm_create_jobtype(callback: types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """Подтверждение создания группы узла"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()
    current_state = await state.get_state()

    jobtype_title = data["jobtype_title"]
    selected_categories = data["selected_categories"]

    await state.clear()

    keyboard = await kb.to_admin_jobs_menu(lang)

    words_for_translator = {
        lang: jobtype_title,
        data['languages_1']: data['translation_1'],
        data['languages_2']: data['translation_2']
    }

    # ONLY for EDIT
    if current_state == EditJobetype.confirm:
        # удаляем старое ключевое слово
        try:
            old_jobtype: Jobtype = data["old_jobtype"]
            keyword = await t.get_key_for_text(old_jobtype.title)
            await t.delete_key_word(keyword)
        except Exception as e:
            await callback.message.edit_text(f"Ошибка при сохранении измененного перевода: {e}", reply_markup=keyboard.as_markup())
            return

    # добавляем новое ключевое слово
    try:
        new_key = await t.add_new_translation(
            words_for_translator
        )
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при сохранении перевода: {e}", reply_markup=keyboard.as_markup())
        return

    # save to DB
    if current_state == AddJobtype.confirm:
        # FOR ADD
        try:
            await AsyncOrm.create_jobtype(new_key, selected_categories, session=session)
        except Exception as e:
            await callback.message.edit_text(f"Ошибка при создании категории узлов {e}", reply_markup=keyboard.as_markup())
    else:
        # FOR EDIT
        try:
            await AsyncOrm.update_jobtype(
                data["jobtype_id"],
                new_key,
                selected_categories,
                session
            )
        except Exception as e:
            await callback.message.edit_text(f"Ошибка при обновлении категории узлов {e}", reply_markup=keyboard.as_markup())

    # FOR ADD
    if current_state == AddJobtype.confirm:
        text = f"✅ Группа узлов \"{jobtype_title}\" успешно создана"
    # FOR EDIT
    else:
        text = f"✅ Группа узлов \"{jobtype_title}\" успешно обновлена"

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


# ADD JOB
@router.callback_query(F.data == "jobs-management|add_job")
async def add_job_start(callback: types.CallbackQuery, tg_id: int, state: FSMContext, session: Any) -> None:
    """Начало добавления job. Выбор категории транспорта"""
    lang = r.get(f"lang:{tg_id}").decode()
    await state.set_state(AddJob.select_category)

    # получаем категории
    categories = await AsyncOrm.get_all_categories(session)

    text = await t.t("select_category", lang)
    keyboard = await kb.select_category_keyboard(categories, "add-job-select-category", lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "add-job-select-category", AddJob.select_category)
async def add_job_get_category(callback: types.CallbackQuery, tg_id: int, state: FSMContext, session: Any) -> None:
    """Получение категории. Выбор jobtype"""
    lang = r.get(f"lang:{tg_id}").decode()
    category_id = int(callback.data.split("|")[1])

    await state.set_state(AddJob.select_jobtype)

    jobtypes = await AsyncOrm.get_job_types_by_category(category_id, session)

    # если группы узлов нет
    if not jobtypes:
        text = await t.t("no_jobtypes", lang)
        error_keyboard = await kb.back_keyboard(lang, "jobs-management|add_job")
        await callback.message.edit_text(text, reply_markup=error_keyboard.as_markup())
        return

    text = await t.t("select_jobtype", lang)
    keyboard = await kb.select_jobtype_keyboard(jobtypes, "add-job-select-jobtype", "jobs-management|add_job", lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "add-job-select-jobtype", AddJob.select_jobtype)
async def add_job_get_jobtype(callback: types.CallbackQuery, tg_id: int, state: FSMContext) -> None:
    """Запись jobtype.id, ввод наименования"""
    lang = r.get(f"lang:{tg_id}").decode()
    jobtype_id = int(callback.data.split("|")[1])

    await state.update_data(jobtype_id=jobtype_id)
    await state.set_state(AddJob.input_job_title)

    text = await t.t("input_job_title", lang)
    keyboard = await kb.back_keyboard(lang, "jobs-management|add_job")

    msg = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_mess=msg)


@router.message(AddJob.input_job_title)
async def add_job_get_job_title(message: types.Message, tg_id: int, state: FSMContext) -> None:
    """Запись названия job"""
    lang = r.get(f"lang:{tg_id}").decode()

    # меняем предыдущее сообщение
    data = await state.get_data()
    try:
        await data["prev_mess"].edit_text(data["prev_mess"].text)
    except Exception:
        pass

    # неверный формат
    if type(message) != types.Message:
        text = await t.t("wrong_text_data", lang)
        error_keyboard = await kb.back_keyboard(lang, "jobs-management|add_job")
        msg = await message.answer(text, reply_markup=error_keyboard.as_markup())
        await state.update_data(prev_mess=msg)
        return

    # меняем стейт
    await state.set_state(AddJob.translate_1)

    # верный формат, сохраняем в стейт
    job_title = message.text
    await state.update_data(job_title=job_title)

    # получаем языки на которые нужно перевести
    languages: list[str] = await neet_to_translate_on(lang)

    # сохраняем требуемые языки в data
    await state.update_data(languages_1=languages[0])
    await state.update_data(languages_2=languages[1])

    text = await t.t("add_translate", lang) + " " + await t.t(languages[0], lang)
    keyboard = await kb.cancel_add_or_edit_job_keyboard(lang)
    msg = await message.answer(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_mess=msg)


@router.message(AddJob.translate_1)
async def add_job_get_translate_1(message: types.Message, tg_id: int, state: FSMContext) -> None:
    """Запись первого перевода"""
    lang = r.get(f"lang:{tg_id}").decode()

    # меняем предыдущее сообщение
    data = await state.get_data()
    try:
        await data["prev_mess"].edit_text(data["prev_mess"].text)
    except Exception:
        pass

    # неверный формат
    if type(message) != types.Message:
        text = await t.t("wrong_text_data", lang)
        error_keyboard = await kb.back_keyboard(lang, "jobs-management|add_job")
        msg = await message.answer(text, reply_markup=error_keyboard.as_markup())
        await state.update_data(prev_mess=msg)
        return

    translation_1 = message.text

    # сохраняем перевод
    await state.update_data(translation_1=translation_1)

    # меняем state
    await state.set_state(AddJob.translate_2)

    text = await t.t("add_translate", lang) + " " + await t.t(data["languages_2"], lang)
    keyboard = await kb.cancel_add_or_edit_job_keyboard(lang)
    msg = await message.answer(text, reply_markup=keyboard.as_markup())

    await state.update_data(prev_mess=msg)


@router.message(AddJob.translate_2)
async def add_job_get_translate_2(message: types.Message, tg_id: int, state: FSMContext) -> None:
    """Запись второго перевода"""
    lang = r.get(f"lang:{tg_id}").decode()

    # меняем предыдущее сообщение
    data = await state.get_data()
    try:
        await data["prev_mess"].edit_text(data["prev_mess"].text)
    except Exception:
        pass

    # неверный формат
    if type(message) != types.Message:
        text = await t.t("wrong_text_data", lang)
        error_keyboard = await kb.back_keyboard(lang, "jobs-management|add_job")
        msg = await message.answer(text, reply_markup=error_keyboard.as_markup())
        await state.update_data(prev_mess=msg)
        return

    translation_2 = message.text

    # сохраняем перевод
    await state.update_data(translation_2=translation_2)

    # меняем state
    await state.set_state(AddJob.confirm)

    # получаем name
    data = await state.get_data()
    job_title = data["job_title"]

    text = await t.t("confirm_job_add", lang)
    keyboard = await kb.add_or_edit_job_confirm_keyboard("add_job_confirmed", lang)
    await message.answer(text.format(job_title), reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "add_job_confirmed", AddJob.confirm)
async def save_job(callback: types.CallbackQuery, tg_id: int, state: FSMContext, session: Any) -> None:
    """Сохранение job"""
    lang = r.get(f"lang:{tg_id}").decode()

    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))

    data = await state.get_data()

    # добавляем в словарь новое слово
    dictionary_for_translator = {
        lang: data['job_title'],
        data['languages_1']: data['translation_1'],
        data['languages_2']: data['translation_2']
    }
    try:
        new_key = await t.add_new_translation(
            dictionary_for_translator
        )
    except Exception as e:
        keyboard = await kb.cancel_add_or_edit_job_keyboard(lang)
        await waiting_message.edit_text(f"Ошибка при сохранении перевода: {e}", reply_markup=keyboard.as_markup())
        await state.clear()
        return

    # сохраняем в бд
    await AsyncOrm.create_job(data["jobtype_id"], new_key, session)

    # сброс стейта
    await state.clear()

    text = await t.t("new_job", lang)
    keyboard = await kb.to_admin_jobs_menu(lang)
    await waiting_message.edit_text(text, reply_markup=keyboard.as_markup())


# EDIT JOB
@router.callback_query(F.data == "jobs-management|edit_job")
async def edit_job_start(callback: types.CallbackQuery, tg_id: int, state: FSMContext, session: Any) -> None:
    """Начало изменения job. Выбор category"""
    lang = r.get(f"lang:{tg_id}").decode()

    await state.set_state(EditJob.select_category)

    # получаем категории
    categories = await AsyncOrm.get_all_categories(session)

    text = await t.t("select_category", lang)
    keyboard = await kb.select_category_keyboard(categories, "edit-job-select-category", lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "edit-job-select-category", EditJob.select_category)
@router.callback_query(F.data.split("|")[0] == "back_from_get_jobtype", EditJob.select_category)
async def edit_job_get_category(callback: types.CallbackQuery, tg_id: int, state: FSMContext, session: Any) -> None:
    """Запись category job. Выбор jobtype"""
    lang = r.get(f"lang:{tg_id}").decode()
    category_id = int(callback.data.split("|")[1])

    await state.set_state(EditJob.select_jobtype)

    jobtypes = await AsyncOrm.get_job_types_by_category(category_id, session)

    # если группы узлов нет
    if not jobtypes:
        text = await t.t("no_jobtypes", lang)
        error_keyboard = await kb.back_keyboard(lang, "jobs-management|edit_job")
        await callback.message.edit_text(text, reply_markup=error_keyboard.as_markup())
        return

    text = await t.t("select_jobtype", lang)
    keyboard = await kb.select_jobtype_keyboard(jobtypes, "edit-job-select-jobtype", "jobs-management|edit_job", lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "edit-job-select-jobtype", EditJob.select_jobtype)
async def get_jobtype_choose_job(callback: types.CallbackQuery, tg_id: int, state: FSMContext, session: Any) -> None:
    """Запись jobtype_id, выбор job"""
    lang = r.get(f"lang:{tg_id}").decode()
    jobtype_id = int(callback.data.split("|")[1])

    await state.set_state(EditJob.select_job)
    await state.update_data(jobtype_id=jobtype_id)

    jobs = await AsyncOrm.get_all_jobs_by_jobtype_id(jobtype_id, session)

    # если работ в группе узлов нет
    if not jobs:
        text = await t.t("no_jobs", lang)
        data = await state.get_data()
        error_keyboard = await kb.back_keyboard(lang, f"back_from_get_jobtype|{data['category_id']}")
        await callback.message.edit_text(text, reply_markup=error_keyboard.as_markup())
        return

    text = await t.t("select_job", lang)
    keyboard = await kb.select_job_keyboard(jobs, lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "edit-job-select-job", EditJob.select_job)
async def get_job_for_edit(callback: types.CallbackQuery, tg_id: int, state: FSMContext) -> None:
    """Запись job id, отправка запроса title"""
    lang = r.get(f"lang:{tg_id}").decode()
    job_id = int(callback.data.split("|")[1])

    await state.update_data(job_id=job_id)
    await state.set_state(EditJob.input_job_title)

    text = await t.t("input_job_title", lang)
    keyboard = await kb.back_keyboard(lang, "jobs-management|edit_job")

    msg = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_mess=msg)


@router.message(EditJob.input_job_title)
async def edit_job_get_job_title(message: types.Message, tg_id: int, state: FSMContext) -> None:
    """Запись нового названия job"""
    lang = r.get(f"lang:{tg_id}").decode()

    # меняем предыдущее сообщение
    data = await state.get_data()
    try:
        await data["prev_mess"].edit_text(data["prev_mess"].text)
    except Exception:
        pass

    # неверный формат
    if type(message) != types.Message:
        text = await t.t("wrong_text_data", lang)
        error_keyboard = await kb.back_keyboard(lang, "jobs-management|add_job")
        msg = await message.answer(text, reply_markup=error_keyboard.as_markup())
        await state.update_data(prev_mess=msg)
        return

    # меняем стейт
    await state.set_state(EditJob.translate_1)

    # верный формат, сохраняем в стейт
    job_title = message.text
    await state.update_data(job_title=job_title)

    # получаем языки на которые нужно перевести
    languages: list[str] = await neet_to_translate_on(lang)

    # сохраняем требуемые языки в data
    await state.update_data(languages_1=languages[0])
    await state.update_data(languages_2=languages[1])

    text = await t.t("add_translate", lang) + " " + await t.t(languages[0], lang)
    keyboard = await kb.cancel_add_or_edit_job_keyboard(lang)
    msg = await message.answer(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_mess=msg)


@router.message(EditJob.translate_1)
async def edit_job_get_translate_1(message: types.Message, tg_id: int, state: FSMContext) -> None:
    """Запись первого перевода"""
    lang = r.get(f"lang:{tg_id}").decode()

    # меняем предыдущее сообщение
    data = await state.get_data()
    try:
        await data["prev_mess"].edit_text(data["prev_mess"].text)
    except Exception:
        pass

    # неверный формат
    if type(message) != types.Message:
        text = await t.t("wrong_text_data", lang)
        error_keyboard = await kb.back_keyboard(lang, "jobs-management|add_job")
        msg = await message.answer(text, reply_markup=error_keyboard.as_markup())
        await state.update_data(prev_mess=msg)
        return

    translation_1 = message.text

    # сохраняем перевод
    await state.update_data(translation_1=translation_1)

    # меняем state
    await state.set_state(EditJob.translate_2)

    text = await t.t("add_translate", lang) + " " + await t.t(data["languages_2"], lang)
    keyboard = await kb.cancel_add_or_edit_job_keyboard(lang)
    msg = await message.answer(text, reply_markup=keyboard.as_markup())

    await state.update_data(prev_mess=msg)


@router.message(EditJob.translate_2)
async def edit_job_get_translate_2(message: types.Message, tg_id: int, state: FSMContext, session: Any) -> None:
    """Запись второго перевода"""
    lang = r.get(f"lang:{tg_id}").decode()

    # меняем предыдущее сообщение
    data = await state.get_data()
    try:
        await data["prev_mess"].edit_text(data["prev_mess"].text)
    except Exception:
        pass

    # неверный формат
    if type(message) != types.Message:
        text = await t.t("wrong_text_data", lang)
        error_keyboard = await kb.back_keyboard(lang, "jobs-management|add_job")
        msg = await message.answer(text, reply_markup=error_keyboard.as_markup())
        await state.update_data(prev_mess=msg)
        return

    translation_2 = message.text

    # сохраняем перевод
    await state.update_data(translation_2=translation_2)

    # меняем state
    await state.set_state(EditJob.confirm)

    # получаем name
    data = await state.get_data()
    job = await AsyncOrm.get_job_by_id(data["job_id"], session)
    old_title = job.title
    new_title = data["job_title"]

    text = await t.t("confirm_job_edit", lang)
    keyboard = await kb.edit_job_confirm_keyboard(lang)
    await message.answer(text.format(old_title, new_title), reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "edit_job_confirmed", EditJob.confirm)
async def save_job(callback: types.CallbackQuery, tg_id: int, state: FSMContext, session: Any) -> None:
    """Сохранение изменения job"""
    lang = r.get(f"lang:{tg_id}").decode()

    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))

    data = await state.get_data()

    # добавляем в словарь новое слово
    dictionary_for_translator = {
        lang: data['job_title'],
        data['languages_1']: data['translation_1'],
        data['languages_2']: data['translation_2']
    }
    try:
        new_key = await t.add_new_translation(
            dictionary_for_translator
        )
    except Exception as e:
        keyboard = await kb.cancel_add_or_edit_job_keyboard(lang)
        await waiting_message.edit_text(f"Ошибка при сохранении перевода: {e}", reply_markup=keyboard.as_markup())
        await state.clear()
        return

    # изменяем в бд
    await AsyncOrm.update_job(data["job_id"], new_key, session)

    # сброс стейта
    await state.clear()

    text = await t.t("updated_job", lang)
    keyboard = await kb.to_admin_jobs_menu(lang)
    await waiting_message.edit_text(text, reply_markup=keyboard.as_markup())









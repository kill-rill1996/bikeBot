from typing import Any

from aiogram import Router, F, types
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext

from cache import r
from routers.states.jobs import AddJobtype, EditJobetype
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

    # save to DB
    if current_state == AddJobtype.confirm:
        # FOR ADD
        try:
            await AsyncOrm.create_jobtype(await t.get_key_for_text(words_for_translator['en']), selected_categories, session=session)
        except Exception as e:
            await callback.message.edit_text(f"Ошибка при создании категории узлов {e}", reply_markup=keyboard.as_markup())
    else:
        # FOR EDIT
        try:
            await AsyncOrm.update_jobtype(
                data["jobtype_id"],
                await t.get_key_for_text(words_for_translator['en']),
                selected_categories,
                session
            )
        except Exception as e:
            await callback.message.edit_text(f"Ошибка при обновлении категории узлов {e}", reply_markup=keyboard.as_markup())

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
        await t.update_translation(
            words_for_translator
        )
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при сохранении перевода: {e}", reply_markup=keyboard.as_markup())
        return

    # FOR ADD
    if current_state == AddJobtype.confirm:
        text = f"✅ Группа узлов \"{jobtype_title}\" успешно создана"
    # FOR EDIT
    else:
        text = f"✅ Группа узлов \"{jobtype_title}\" успешно обновлена"

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())














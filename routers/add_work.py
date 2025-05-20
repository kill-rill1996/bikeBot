from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from cache import r
from utils.translator import translator as t
from utils.validations import is_valid_vehicle_number
from routers.states.add_work import AddWorkFSM

from routers.keyboards import add_works as kb

router = Router()


@router.callback_query(F.data == "works|add-works")
async def add_work_menu(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Меню добавить работу. Меню выбора категории"""
    tg_id = str(callback.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()

    # начало стейта AddWorkFSM
    await state.set_state(AddWorkFSM.vehicle_category)

    text = t.t("select_category", lang)
    await callback.message.edit_text(text, reply_markup=kb.add_works_menu_keyboard(lang).as_markup())


@router.callback_query(F.data.split("|")[0] == "vehicle_category", AddWorkFSM.vehicle_category)
@router.callback_query(F.data.split("|")[0] == "back_to_choose_subcategory")
async def add_work_vehicle_category(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Запись категории. Меню выбора подкатегории"""
    vehicle_category = callback.data.split("|")[1]
    tg_id = str(callback.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()

    # запись категории в стейт
    await state.update_data(vehicle_category=vehicle_category)

    # у категории велосипеды еще необходима подкатегория
    # также сюда попадает возврат из ввода номера велосипеда
    if vehicle_category == "bicycles":
        # устанавливаем стейт
        await state.set_state(AddWorkFSM.vehicle_subcategory)

        # предлагаем выбрать подкатегорию
        text = t.t("select_subcategory", lang)
        await callback.message.edit_text(text, reply_markup=kb.select_subcategory_keyboard(lang).as_markup())

    # категория не велосипед
    else:
        # пропускаем подкатегорию, номер и переходим в стейт AddWorkFSM.work_category
        await state.set_state(AddWorkFSM.work_category)

        text = t.t("select_work_category", lang)
        await callback.message.edit_text(text, reply_markup=kb.select_work_category(lang).as_markup())


@router.callback_query(F.data.split("|")[0] == "vehicle_subcategory", AddWorkFSM.vehicle_subcategory)
async def add_work_vehicle_subcategory(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Запись подкатегории. Выбор номера"""
    vehicle_subcategory = callback.data.split("|")[1]
    tg_id = str(callback.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()

    # записываем подкатегорию
    await state.update_data(vehicle_subcategory=vehicle_subcategory)

    # меняем стейт
    await state.set_state(AddWorkFSM.vehicle_number)

    # TODO перевести текст для всех
    text = f"Введите номер велосипеда для подкатегории {vehicle_subcategory}"

    msg = await callback.message.edit_text(text, reply_markup=kb.select_bicycle_number(lang).as_markup())
    await state.update_data(prev_mess=msg)


@router.message(AddWorkFSM.vehicle_number)
async def add_work_vehicle_number(message: types.Message, state: FSMContext) -> None:
    """Валидация и запись номера и запись его в стейт"""
    vehicle_number = message.text
    tg_id = str(message.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()

    # удаляем предыдущее сообщение
    data = await state.get_data()
    try:
        await data["prev_mess"].delete()
    except Exception:
        pass

    # если номер неправильный
    if not is_valid_vehicle_number(vehicle_number):
        # отправляем сообщение о необходимости ввести номер еще раз
        text = f"Номер введен неправильно для категории {data['vehicle_subcategory']}\n" \
               f"Необходимо отправить число от 1 до 100, отправьте номер еще раз"
        msg = await message.answer(text, reply_markup=kb.select_bicycle_number(lang).as_markup())

        # записываем в предыдущие сообщения
        await state.update_data(prev_mess=msg)

    # если номер правильный
    else:
        # записываем номер в стейт
        await state.update_data(vehicle_number=vehicle_number)

        # переходим в стейт AddWorkFSM.work_category
        await state.set_state(AddWorkFSM.work_category)

        text = t.t("select_work_category", lang)
        await message.answer(text, reply_markup=kb.select_work_category(lang).as_markup())


@router.callback_query(F.data.split("|")[0] == "work_category", AddWorkFSM.work_category)
async def add_work_category(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Запись категории работы"""
    work_category = callback.data.split("|")[1]
    tg_id = str(callback.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()

    # TODO если выбрано прочие
    if work_category == "other":
        pass

    # записываем категорию работы
    await state.update_data(work_category=work_category)

    text = t.t("select_operation", lang)
    await callback.message.edit_text(text)



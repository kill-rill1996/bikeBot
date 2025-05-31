from schemas.search import OperationJobsUserLocation
from utils.translator import translator as t
from utils.date_time_service import convert_date_time


async def search_transport_result(operations: list[OperationJobsUserLocation], lang: str) -> str:
    """Сообщение о результатах поиска"""
    text = await t.t("searched_work_count", lang)
    message = f"<b>{text.format(len(operations))}\n\n</b>"

    for operation in operations:
        date: str = convert_date_time(operation.created_at)[0]
        category_title = await t.t(operation.category_title, lang)

        message += f"{date}: {operation.id} | {category_title} | {operation.subcategory_title}-{operation.serial_number} | "

        # добавляем все названия работ
        for job in operation.jobs:
            message += await t.t(job[0], lang) + " | "

        message += f"{await t.t(operation.role, lang)} {operation.username}\n\n"

    return message


async def operation_detail_message(operation: OperationJobsUserLocation, lang: str) -> str:
    """Вывод деталей по выбранной работе"""
    message = await t.t("selected_work_details", lang) + "\n\n"
    date = convert_date_time(operation.created_at)[0]
    message += f"ID: {operation.id}, {date}, {operation.duration} {await t.t('minutes', lang)}\n{await t.t(operation.category_title, lang)} {operation.subcategory_title}-{operation.serial_number}\n\n"

    for job in operation.jobs:
        message += f"\t\t• {await t.t(job[1], lang)} -> {await t.t(job[0], lang)}\n"

    message += f"\n{operation.location}\n{operation.username}: " \
               f"\"<i>{operation.comment}</i>\""

    return message

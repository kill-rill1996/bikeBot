from schemas.categories_and_jobs import Category
from schemas.operations import OperationJobs
from utils.translator import translator as t


async def statistic_message(lang: str, all_operations: list[OperationJobs], categories: list[Category]) -> str:
    """Вывод сообщения со статистикой за определенный период"""
    message = ""
    all_jobs_count = 0

    for category in categories:
        # кол-во работ по категории (например Велосипеды - 5)
        categories_operations = [operation for operation in all_operations if operation.transport_category == category.title]

        # кол-во jobs для этой категории
        jobs_count = sum([len(operation.jobs_titles) for operation in categories_operations])

        message += f"{category.emoji + ' ' if category.emoji else ''}{await t.t(category.title, lang)}: {jobs_count} {await t.t('works', lang)}\n"

        # проходим по операциям, чтобы внести их в список
        works_for_transport = {}
        for operation in categories_operations:

            # объединяем по подкатегориям и серийному номеру например U-15
            key = f"{operation.transport_subcategory}-{operation.serial_number}"
            if key in works_for_transport.keys():
                works_for_transport[key] += len(operation.jobs_titles)
            else:
                works_for_transport[key] = len(operation.jobs_titles)

        for key, value in works_for_transport.items():
            message += f"{key}: {value} {await t.t('works', lang)}, "

        # добавляем количество работ в этой категории к общему
        all_jobs_count += jobs_count

        # убираем точку и пробел для последней записи
        if categories_operations:
            message = message[:-2]
        message += "\n\n"

    # общее кол-во работ (jobs)
    message += f"{await t.t('total_number_of_works', lang)}: {all_jobs_count}\n"

    # среднее время
    full_time = sum([operation.duration for operation in all_operations])
    average_time = int(full_time / all_jobs_count)
    message += f"{await t.t('average_time', lang)}: {average_time} {await t.t('minutes', lang)}\n"

    # общее время
    message += f"{await t.t('total_time', lang)}: {full_time} {await t.t('minutes', lang)}"

    return message


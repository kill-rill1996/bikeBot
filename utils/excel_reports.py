import datetime
import os

from openpyxl.styles import Font, PatternFill, Border, Side, Alignment

from schemas.reports import OperationWithJobs
from utils.date_time_service import convert_date_time
from utils.translator import translator as t
import pandas as pd


async def individual_mechanic_excel_report(operations: list[OperationWithJobs], mechanic_username: str,
                                           start_date: datetime.datetime, end_date: datetime.datetime,
                                           report_type: str, lang: str) -> str:
    """Генерация excel отчета. Возвращает путь к файлу"""
    # Создаем директорию для отчетов, если ее нет
    os.makedirs("reports", exist_ok=True)

    # Цвета
    COLOR_DARK_BLUE = "203764"  # Темно-синий текст
    COLOR_LIGHT_BLUE = "D9E1F2"  # Светло-синий фон
    COLOR_LIGHT_GREEN = "E2EFDA"  # Светло-зеленый фон
    COLOR_LIGHT_YELLOW = "FFF2CC"  # Светло-желтый фон
    COLOR_LIGHT_RED = "FFCCCC"  # Светло-красный фон
    COLOR_LIGHT_GRAY = "F2F2F2"  # Светло-серый фон
    COLOR_WHITE = "FFFFFF"  # Белый фон

    # Стили границ
    BORDER_STYLE_THIN = "thin"
    BORDER_STYLE_MEDIUM = "medium"

    # Выравнивание
    ALIGN_CENTER = "center"
    ALIGN_LEFT = "left"
    ALIGN_RIGHT = "right"

    # Путь к файлу Excel в зависимости от типа отчета
    start_date = convert_date_time(start_date, with_tz=True)[0]
    end_date = convert_date_time(end_date, with_tz=True)[0]
    excel_path = f"reports/{report_type}_{start_date}_{end_date}.xlsx"
    sheet_name = "mechanic_report"
    title = f"📆 {await t.t(report_type, lang)} {start_date} - {end_date} {mechanic_username}"

    data = []

    columns = [
        "ID",
        await t.t('excel_date', lang),
        await t.t('excel_time', lang),
        await t.t('excel_transport', lang),
        await t.t('excel_jobtype', lang),
        await t.t('excel_jobs', lang),
        await t.t('excel_comment', lang),
        await t.t('excel_avg_time', lang)]
    data.append(columns)

    # формируем данные
    for operation in operations:
        for job in operation.jobs:
            data.append(
                [
                    # ID
                    f"{operation.id}",
                    # дата
                    f"{convert_date_time(operation.created_at, with_tz=True)[0]}",
                    # время на работу == среднему потому что на каждую операцию отдельная строка
                    f"{round(operation.duration / len(operation.jobs))}",
                    # траспорт с категорией и номером
                    f"{await t.t(operation.transport_category, lang)} {operation.transport_subcategory}-{operation.transport_serial_number}",
                    # группа узлов
                    f"{await t.t(operation.jobs[0].jobtype_title, lang)}",
                    # работы
                    f"{await t.t(job.title, lang)}",
                    # комментарий
                    f"{operation.comment if operation.comment else '-'}",
                    # среднее время на работу
                    f"{round(operation.duration / len(operation.jobs))}"
                ]
            )

    # Добавляем пустую строку между разделами
    data.append(["", "", "", "", "", "", "", ""])

    jobs_count = sum([len(operation.jobs) for operation in operations])
    duration_sum = str(sum([operation.duration for operation in operations]))
    # количество работ
    data.append([f"{await t.t('number_of_works', lang)}", "", f"{jobs_count}"])
    # общее время на работы
    data.append([f"{await t.t('total_time_spent', lang)}", "", f"{duration_sum} {await t.t('minutes', lang)}"])

    # Создаем DataFrame с заголовками
    df = pd.DataFrame(data)

    # Записываем в Excel
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Форматирование
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        # Настройка ширины столбцов
        worksheet.column_dimensions['A'].width = 15
        worksheet.column_dimensions['B'].width = 20
        worksheet.column_dimensions['C'].width = 15
        worksheet.column_dimensions['D'].width = 25
        worksheet.column_dimensions['E'].width = 35
        worksheet.column_dimensions['F'].width = 45
        worksheet.column_dimensions['G'].width = 40
        worksheet.column_dimensions['H'].width = 20

        # Заголовок отчета с улучшенным форматированием
        title_cell = worksheet.cell(row=1, column=1)
        title_cell.value = title
        title_cell.font = Font(bold=True, size=14, color=COLOR_DARK_BLUE)  # Темно-синий текст

        # объединяем для заголовка
        worksheet.merge_cells('A1:H1')

        # делаем заголовок по центру
        title_cell.alignment = Alignment(horizontal=ALIGN_CENTER)

        # Добавляем светло-синий фон для заголовка
        title_cell.fill = PatternFill(start_color=COLOR_LIGHT_BLUE, end_color=COLOR_LIGHT_BLUE, fill_type="solid")

        # Добавляем границу для заголовка
        title_cell.border = Border(
            left=Side(style=BORDER_STYLE_MEDIUM),
            right=Side(style=BORDER_STYLE_MEDIUM),
            top=Side(style=BORDER_STYLE_MEDIUM),
            bottom=Side(style=BORDER_STYLE_MEDIUM)
        )

        # делаем названия колонок по центру и добавляем границы
        for i in range(8):
            column_cell = worksheet.cell(row=2, column=i+1)
            column_cell.alignment = Alignment(horizontal=ALIGN_CENTER)
            column_cell.border = Border(
                left=Side(style=BORDER_STYLE_THIN),
                right=Side(style=BORDER_STYLE_THIN),
                bottom=Side(style=BORDER_STYLE_THIN)
            )

    return excel_path

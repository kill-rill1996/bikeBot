import datetime
import os

from openpyxl.styles import Font, PatternFill, Border, Side

from utils.date_time_service import convert_date_time
from utils.translator import translator as t
import pandas as pd


async def generate_excel_report(report_data: dict, start_date: datetime.datetime, end_date: datetime.datetime, report_type: str, lang: str) -> str:
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
    sheet_name = report_type[:10]
    title = f"{await t.t(report_type, lang)} {start_date}-{end_date}"

    data = []

    columns = [await t.t('excel_date', lang), await t.t('excel_time', lang), await t.t('excel_transport', lang),
                await t.t('excel_jobs', lang), await t.t('excel_comment', lang), await t.t('excel_avg_time', lang)]

    # Добавляем пустую строку между заголовком и первым видом транспорта
    data.append(["", "", "", "", "", ""])

    data.append(["31.05.2025", "34 мин", "Велосипеды U-7", "Замена тормозных колодок\nНастройка тормозов", "ossoos",
                 "23 мин"])

    data.append(
        ["31.05.2025", "34 мин", "Велосипеды U-7", "Замена тормозных колодок\nНастройка тормозов", "ossoos", "23 мин"])

    data.append(
        ["31.05.2025", "34 мин", "Велосипеды U-7", "Замена тормозных колодок\nНастройка тормозов", "ossoos", "23 мин"])

    # Создаем DataFrame с заголовками
    df = pd.DataFrame(data, columns=columns)

    # Записываем в Excel
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name[:10], index=False)

        # Форматирование
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        # Настройка ширины столбцов
        worksheet.column_dimensions['A'].width = 46  # equipment_type - ширина для слова "электровелосипеды"
        worksheet.column_dimensions['B'].width = 25  # percentage - расширенная для максимальной длины текста
        worksheet.column_dimensions['C'].width = 15  # quantity

        # Заголовок отчета с улучшенным форматированием
        title_cell = worksheet.cell(row=1, column=1)
        title_cell.value = title
        title_cell.font = Font(bold=True, size=14, color=COLOR_DARK_BLUE)  # Темно-синий текст

        # Добавляем светло-синий фон для заголовка
        title_cell.fill = PatternFill(start_color=COLOR_LIGHT_BLUE, end_color=COLOR_LIGHT_BLUE, fill_type="solid")

        # Добавляем границу для заголовка
        title_cell.border = Border(left=Side(style=BORDER_STYLE_MEDIUM), right=Side(style=BORDER_STYLE_MEDIUM),
            top=Side(style=BORDER_STYLE_MEDIUM), bottom=Side(style=BORDER_STYLE_MEDIUM))


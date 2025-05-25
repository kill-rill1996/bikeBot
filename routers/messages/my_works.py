from schemas.operations import OperationDetails
from utils.translator import translator as t
from utils.date_time_service import convert_date_time


async def work_detail_message(lang: str, work: OperationDetails) -> str:
    """Сообщения для вывода информации по работе"""
    local_date = convert_date_time(work.created_at)[0]
    comment = work.comment if work.comment else "-"

    message = await t.t("work_details", lang) + "\n" \
              + await t.t("date", lang) + f" {local_date}, ID: {work.id}\n" \
              + await t.t("vehicle", lang) + ": " + await t.t(f"{work.transport_category}", lang) + " "\
              + f"{work.transport_subcategory}-{work.serial_number}\n" \
              + await t.t("operation", lang) + " " + await t.t(work.job_title, lang) + "\n" \
              + await t.t("time", lang) + " " + f"{work.duration}" + " " + await t.t("minutes", lang) + "\n"\
              + await t.t("comment", lang) + " " + comment

    return message


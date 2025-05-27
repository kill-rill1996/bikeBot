from schemas.operations import OperationDetailJobs
from utils.translator import translator as t
from utils.date_time_service import convert_date_time


async def work_detail_message(lang: str, work: OperationDetailJobs) -> str:
    """Сообщения для вывода информации по работе"""
    local_date = convert_date_time(work.created_at)[0]
    comment = work.comment if work.comment else "-"

    message = await t.t("work_details", lang) + "\n" \
              + await t.t("date", lang) + f" {local_date}, ID: {work.id}\n" \
              + await t.t("vehicle", lang) + ": " + await t.t(f"{work.transport_category}", lang) + " "\
              + f"{work.transport_subcategory}-{work.serial_number}\n" \
              + await t.t("time", lang) + " " + f"{work.duration}" + " " \
              + await t.t("minutes", lang) + "\n" \
              + await t.t("operation", lang) + "\n" \

    for job_title in work.jobs_titles:
        message += f"- {await t.t(job_title, lang)}\n"

    message += "\n" + await t.t("comment", lang) + " " + f"<i>{comment}</i>"

    return message


from aiogram import Router

from routers.start import router as start_router
from routers.menu import router as menu_router
from routers.works import router as work_router
from routers.add_work import router as add_work_router
from routers.settings import router as settings_router
from routers.statistic import router as statistic_router
from routers.search import router as search_router
from routers.admin.menu import router as admin_menu_router
from routers.admin.reports import router as admin_reports_router


main_router = Router()

main_router.include_routers(
    start_router,
    menu_router,
    work_router,
    add_work_router,
    settings_router,
    admin_menu_router,
    admin_reports_router,
    statistic_router,
    search_router,
)
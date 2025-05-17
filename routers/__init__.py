from aiogram import Router

from routers.start import router as start_router
from routers.menu import router as menu_router

main_router = Router()

main_router.include_routers(
    start_router,
    menu_router,
)
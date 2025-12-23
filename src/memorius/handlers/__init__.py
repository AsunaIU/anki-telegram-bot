from aiogram import Router

from memorius.handlers.user import router as user_router

router = Router()
router.include_router(user_router)


__all__ = [
    "router",
]

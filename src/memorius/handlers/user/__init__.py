from aiogram import Router

from memorius.handlers.user import card, deck, help, language, session, start, statistics

router = Router()
router.include_routers(
    start.router, deck.router, card.router, session.router, statistics.router, help.router, language.router
)

__all__ = [
    "router",
]

from aiogram import Router

from memorius.handlers.user import card, deck, help, session, start, statistics

router = Router()
router.include_routers(
    start.router,
    deck.router,
    card.router,
    session.router,
    statistics.router,
    help.router,
)

__all__ = [
    "router",
]

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub

from memorius.config import settings
from memorius.database.database import async_session_maker
from memorius.handlers import router as main_router
from memorius.middlewares.database import DatabaseMiddleware
from memorius.middlewares.translate import TranslateMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


translator_hub = TranslatorHub(
    locales_map={
        "ru": ("ru", "en"),  # Russian with English fallback
        "en": ("en",),  # English only
    },
    translators=[
        FluentTranslator(
            locale="ru",
            translator=FluentBundle.from_files(
                locale="ru-RU",
                filenames=[
                    "src/memorius/i18n/ru/cards.ftl",
                    "src/memorius/i18n/ru/common.ftl",
                    "src/memorius/i18n/ru/decks.ftl",
                    "src/memorius/i18n/ru/help.ftl",
                    "src/memorius/i18n/ru/review.ftl",
                    "src/memorius/i18n/ru/start.ftl",
                    "src/memorius/i18n/ru/statistics.ftl",
                ],
            ),
        ),
        FluentTranslator(
            locale="en",
            translator=FluentBundle.from_files(
                locale="en-US",
                filenames=[
                    "src/memorius/i18n/en/cards.ftl",
                    "src/memorius/i18n/en/common.ftl",
                    "src/memorius/i18n/en/decks.ftl",
                    "src/memorius/i18n/en/help.ftl",
                    "src/memorius/i18n/en/review.ftl",
                    "src/memorius/i18n/en/start.ftl",
                    "src/memorius/i18n/en/statistics.ftl",
                ],
            ),
        ),
    ],
    root_locale="en",
)


async def main() -> None:
    session = AiohttpSession()
    bot = Bot(token=settings.BOT_TOKEN, session=session, default=DefaultBotProperties(parse_mode="HTML"))

    dp = Dispatcher(t_hub=translator_hub)

    dp.update.middleware(DatabaseMiddleware(async_session_maker))
    dp.update.middleware(TranslateMiddleware())

    dp.include_router(main_router)

    try:
        logger.info("Starting bot...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

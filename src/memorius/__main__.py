import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub

from memorius.config import settings
from memorius.database.database import async_session_maker
from memorius.middleware import DatabaseMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


t_hub = TranslatorHub(
    {"ru": ("ru",)},
    translators=[
        FluentTranslator(
            "ru",
            translator=FluentBundle.from_files("ru-RU", filenames=["src/i18n/ru/text.ftl", "src/i18n/ru/button.ftl"]),
        )
    ],
)


async def main() -> None:
    session = AiohttpSession()
    bot = Bot(token=settings.BOT_TOKEN, session=session, default=DefaultBotProperties(parse_mode="HTML"))

    dp = Dispatcher()

    dp.update.middleware(DatabaseMiddleware(async_session_maker))

    # Routers

    try:
        logger.info("Starting bot...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

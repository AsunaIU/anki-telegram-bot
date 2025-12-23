from collections.abc import Awaitable, Callable
from contextlib import suppress
from typing import Any

from aiogram import BaseMiddleware, Router
from aiogram.types import TelegramObject, User
from fluentogram import TranslatorHub

from memorius.database.repositories import UserRepository

router = Router()


class TranslateMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        session = data.get("session")

        language_code = "ru"

        if user and session:
            user_repo = UserRepository(session)
            with suppress(Exception):
                db_user = await user_repo.get_or_create_user(
                    user_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                )
                if db_user.language_code:
                    language_code = db_user.language_code

        # Simplified nested ifs
        if user and not language_code and user.language_code:
            if user.language_code.startswith("ru"):
                language_code = "ru"
            elif user.language_code.startswith("en"):
                language_code = "en"

        t_hub: TranslatorHub = data["t_hub"]
        data["locale"] = t_hub.get_translator_by_locale(language_code)

        return await handler(event, data)

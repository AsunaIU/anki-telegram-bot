from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Update
from fluentogram import TranslatorHub


class TranslateMiddleware(BaseMiddleware):
    """
    Fluentogram translation middleware
    """

    async def __call__(
        self, handler: Callable[[Update, dict[str, Any]], Awaitable[Any]], event: Update, data: dict[str, Any]
    ) -> Any:
        language = data["user"].language_code if "user" in data else "ru"

        hub: TranslatorHub = data.get("t_hub")

        data["locale"] = hub.get_translator_by_locale(language)

        return await handler(event, data)

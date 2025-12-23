from aiogram import F, Router
from aiogram.types import Message
from fluentogram import TranslatorRunner

from memorius.keyboards import get_back_to_menu_keyboard

router = Router()


@router.message(
    F.text.in_(
        [
            "❓ Помощь",  # Russian
            "❓ Help",  # English
        ]
    )
)
async def show_help(message: Message, locale: TranslatorRunner):
    """Show help message"""
    await message.answer(locale.help_text(), reply_markup=get_back_to_menu_keyboard(locale))

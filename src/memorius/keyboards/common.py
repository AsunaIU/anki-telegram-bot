from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluentogram import TranslatorRunner


def get_cancel_keyboard(locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard with cancel button"""
    builder = InlineKeyboardBuilder()
    builder.button(text=locale.btn_cancel(), callback_data="cancel")
    return builder.as_markup()

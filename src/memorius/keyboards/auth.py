from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from fluentogram import TranslatorRunner


def get_contact_keyboard(locale: TranslatorRunner) -> ReplyKeyboardMarkup:
    """Keyboard for sharing contact information"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=locale.btn_share_contact(), request_contact=True))
    return builder.as_markup(resize_keyboard=True)

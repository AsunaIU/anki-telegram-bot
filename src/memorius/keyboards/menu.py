from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from fluentogram import TranslatorRunner


def get_main_menu_keyboard(locale: TranslatorRunner) -> ReplyKeyboardMarkup:
    """Main menu keyboard with primary bot functions"""
    builder = ReplyKeyboardBuilder()
    builder.button(text=locale.create_deck())
    builder.button(text=locale.my_decks())
    builder.button(text=locale.statistics())
    builder.button(text=locale.help())
    builder.button(text=locale.language())
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_back_to_menu_keyboard(locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard with back to menu button"""
    builder = InlineKeyboardBuilder()
    builder.button(text=locale.btn_back_menu(), callback_data="main_menu")
    return builder.as_markup()


def get_statistics_period_keyboard(locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard for selecting statistics time period"""
    builder = InlineKeyboardBuilder()
    builder.button(text=locale.btn_period_week(), callback_data="stats_7")
    builder.button(text=locale.btn_period_month(), callback_data="stats_30")
    builder.button(text=locale.btn_period_three_months(), callback_data="stats_90")
    builder.button(text=locale.btn_back_menu(), callback_data="main_menu")
    builder.adjust(3, 1)
    return builder.as_markup()


def get_language_keyboard(locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard for language selection"""
    keyboard = [
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        ],
        [InlineKeyboardButton(text=locale.btn_back_menu(), callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

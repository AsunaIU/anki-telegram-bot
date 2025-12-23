from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluentogram import TranslatorRunner


def get_card_list_keyboard(cards: list, action: str, deck_id: int, locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard with list of cards for editing or deleting"""
    builder = InlineKeyboardBuilder()
    for card in cards:
        question_preview = card.question[:30] + "..." if len(card.question) > 30 else card.question
        builder.button(text=question_preview, callback_data=f"{action}_card_id_{card.id}")
    builder.button(text=locale.btn_back(), callback_data=f"deck_{deck_id}")
    builder.adjust(1)
    return builder.as_markup()


def get_card_type_keyboard(locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard for selecting card type"""
    keyboard = [
        [InlineKeyboardButton(text=locale.card_type_text(), callback_data="card_type_text")],
        [InlineKeyboardButton(text=locale.card_type_variants(), callback_data="card_type_variants")],
        [InlineKeyboardButton(text=locale.btn_cancel(), callback_data="cancel")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_review_keyboard(locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard for card review session"""
    builder = InlineKeyboardBuilder()
    builder.button(text=locale.btn_show_answer(), callback_data="show_answer")
    builder.button(text=locale.btn_skip(), callback_data="skip_card")
    builder.adjust(1)
    return builder.as_markup()


def get_difficulty_keyboard(locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard for rating answer difficulty"""
    builder = InlineKeyboardBuilder()
    builder.button(text=locale.btn_easy(), callback_data="difficulty_easy")
    builder.button(text=locale.btn_medium(), callback_data="difficulty_medium")
    builder.button(text=locale.btn_hard(), callback_data="difficulty_hard")
    builder.adjust(3)
    return builder.as_markup()


def get_variant_keyboard(card, locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard for variant answer selection"""
    keyboard = []

    for i in range(1, 5):
        variant = getattr(card, f"variant_{i}", None)
        if variant:
            keyboard.append([InlineKeyboardButton(text=f"{i}", callback_data=f"variant_answer_{i}")])

    keyboard.append([InlineKeyboardButton(text=locale.skip_button(), callback_data="skip_card")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

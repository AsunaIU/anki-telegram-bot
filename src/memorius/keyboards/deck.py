from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluentogram import TranslatorRunner


def get_deck_list_keyboard(decks: list, locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard with list of user's decks"""
    builder = InlineKeyboardBuilder()
    for deck in decks:
        cards_count = len(deck.cards) if hasattr(deck, "cards") else 0
        builder.button(text=f"{deck.name} ({cards_count} {locale.cards_short()})", callback_data=f"deck_{deck.id}")
    builder.button(text=locale.btn_back_menu(), callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


def get_deck_actions_keyboard(deck_id: int, has_cards: bool, locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard with available actions for a deck"""
    builder = InlineKeyboardBuilder()

    if has_cards:
        builder.button(text=locale.btn_open_deck(), callback_data=f"open_deck_{deck_id}")
        builder.button(text=locale.btn_start_session(), callback_data=f"start_session_{deck_id}")

    builder.button(text=locale.btn_add_card(), callback_data=f"add_card_{deck_id}")

    if has_cards:
        builder.button(text=locale.btn_edit_card(), callback_data=f"edit_card_{deck_id}")
        builder.button(text=locale.btn_delete_card(), callback_data=f"delete_card_{deck_id}")

    builder.button(text=locale.btn_delete_deck(), callback_data=f"delete_deck_{deck_id}")
    builder.button(text=locale.btn_back_to_decks(), callback_data="my_decks")
    builder.adjust(1)
    return builder.as_markup()


def get_after_create_deck_keyboard(deck_id: int, locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard shown after deck creation"""
    builder = InlineKeyboardBuilder()
    builder.button(text=locale.btn_add_card(), callback_data=f"add_card_{deck_id}")
    builder.button(text=locale.btn_back_menu(), callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

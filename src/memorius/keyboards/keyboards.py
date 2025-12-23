from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from fluentogram import TranslatorRunner


def get_contact_keyboard(locale: TranslatorRunner) -> ReplyKeyboardMarkup:
    """Keyboard for sharing contact"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=locale.btn_share_contact(), request_contact=True))
    return builder.as_markup(resize_keyboard=True)


def get_main_menu_keyboard(locale: TranslatorRunner) -> ReplyKeyboardMarkup:
    """Main menu keyboard"""
    builder = ReplyKeyboardBuilder()
    builder.button(text=locale.create_deck())
    builder.button(text=locale.my_decks())
    builder.button(text=locale.statistics())
    builder.button(text=locale.help())
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_deck_list_keyboard(decks: list, locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard with list of decks"""
    builder = InlineKeyboardBuilder()
    for deck in decks:
        cards_count = len(deck.cards) if hasattr(deck, "cards") else 0
        builder.button(text=f"{deck.name} ({cards_count} {locale.cards_short()})", callback_data=f"deck_{deck.id}")
    builder.button(text=locale.btn_back_menu(), callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


def get_deck_actions_keyboard(deck_id: int, has_cards: bool, locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard with deck actions"""
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


def get_card_list_keyboard(cards: list, action: str, deck_id: int, locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard with list of cards for editing or deleting"""
    builder = InlineKeyboardBuilder()
    for card in cards:
        question_preview = card.question[:30] + "..." if len(card.question) > 30 else card.question
        builder.button(text=question_preview, callback_data=f"{action}_card_id_{card.id}")
    builder.button(text=locale.btn_back(), callback_data=f"deck_{deck_id}")
    builder.adjust(1)
    return builder.as_markup()


def get_review_keyboard(locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard for card review"""
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


def get_cancel_keyboard(locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard with cancel button"""
    builder = InlineKeyboardBuilder()
    builder.button(text=locale.btn_cancel(), callback_data="cancel")
    return builder.as_markup()


def get_back_to_menu_keyboard(locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard with back to menu button"""
    builder = InlineKeyboardBuilder()
    builder.button(text=locale.btn_back_menu(), callback_data="main_menu")
    return builder.as_markup()


def get_after_create_deck_keyboard(deck_id: int, locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard after deck creation"""
    builder = InlineKeyboardBuilder()
    builder.button(text=locale.btn_add_card(), callback_data=f"add_card_{deck_id}")
    builder.button(text=locale.btn_back_menu(), callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


def get_statistics_period_keyboard(locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard for selecting statistics period"""
    builder = InlineKeyboardBuilder()
    builder.button(text=locale.btn_period_week(), callback_data="stats_7")
    builder.button(text=locale.btn_period_month(), callback_data="stats_30")
    builder.button(text=locale.btn_period_three_months(), callback_data="stats_90")
    builder.button(text=locale.btn_back_menu(), callback_data="main_menu")
    builder.adjust(3, 1)
    return builder.as_markup()


def get_card_type_keyboard(locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard for selecting card type"""
    keyboard = [
        [InlineKeyboardButton(text=locale.card_type_text(), callback_data="card_type_text")],
        [InlineKeyboardButton(text=locale.card_type_variants(), callback_data="card_type_variants")],
        [InlineKeyboardButton(text=locale.btn_cancel(), callback_data="cancel")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_variant_keyboard(card, locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Keyboard for variant answers"""
    keyboard = []

    for i in range(1, 5):
        variant = getattr(card, f"variant_{i}", None)
        if variant:
            keyboard.append([InlineKeyboardButton(text=f"{i}", callback_data=f"variant_answer_{i}")])

    keyboard.append([InlineKeyboardButton(text=locale.skip_button(), callback_data="skip_card")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

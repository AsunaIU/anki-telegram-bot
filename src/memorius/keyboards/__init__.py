from .auth import get_contact_keyboard
from .card import (
    get_card_list_keyboard,
    get_card_type_keyboard,
    get_difficulty_keyboard,
    get_review_keyboard,
    get_variant_keyboard,
)
from .common import get_cancel_keyboard
from .deck import (
    get_after_create_deck_keyboard,
    get_deck_actions_keyboard,
    get_deck_list_keyboard,
)
from .menu import (
    get_back_to_menu_keyboard,
    get_language_keyboard,
    get_main_menu_keyboard,
    get_statistics_period_keyboard,
)

__all__ = [
    # Auth
    "get_contact_keyboard",
    # Deck
    "get_after_create_deck_keyboard",
    "get_deck_actions_keyboard",
    "get_deck_list_keyboard",
    # Card
    "get_card_list_keyboard",
    "get_card_type_keyboard",
    "get_difficulty_keyboard",
    "get_review_keyboard",
    "get_variant_keyboard",
    # Menu
    "get_back_to_menu_keyboard",
    "get_language_keyboard",
    "get_main_menu_keyboard",
    "get_statistics_period_keyboard",
    # Common
    "get_cancel_keyboard",
]

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from memorius.database.repositories import CardRepository, DeckRepository
from memorius.keyboards import (
    get_after_create_deck_keyboard,
    get_back_to_menu_keyboard,
    get_cancel_keyboard,
    get_deck_actions_keyboard,
    get_deck_list_keyboard,
)
from memorius.utils import CreateDeck, validate_deck_name

router = Router()


@router.message(
    F.text.in_(
        [
            "➕ Создать колоду",  # Russian
            "➕ Create deck",  # English
        ]
    )
)
async def create_deck_start(message: Message, state: FSMContext, locale: TranslatorRunner):
    """Start deck creation"""
    await state.set_state(CreateDeck.waiting_for_name)
    await message.answer(locale.enter_deck_name(), reply_markup=get_cancel_keyboard(locale))


@router.message(CreateDeck.waiting_for_name)
async def create_deck_finish(message: Message, state: FSMContext, session: AsyncSession, locale: TranslatorRunner):
    """Finish deck creation"""
    deck_name = message.text.strip()

    if not validate_deck_name(deck_name):
        await message.answer(locale.deck_invalid_name(), reply_markup=get_cancel_keyboard(locale))
        return

    deck_repo = DeckRepository(session)
    deck = await deck_repo.create_deck(user_id=message.from_user.id, name=deck_name)

    await state.clear()
    await message.answer(
        locale.deck_created(name=deck_name), reply_markup=get_after_create_deck_keyboard(deck.id, locale)
    )


@router.message(
    F.text.in_(
        [
            "📚 Мои колоды",  # Russian
            "📚 My decks",  # English
        ]
    )
)
@router.callback_query(F.data == "my_decks")
async def show_my_decks(event: Message | CallbackQuery, session: AsyncSession, locale: TranslatorRunner):
    """Show user's decks"""
    deck_repo = DeckRepository(session)
    decks = await deck_repo.get_user_decks(event.from_user.id)

    if not decks:
        text = locale.no_decks()
        keyboard = get_back_to_menu_keyboard(locale)
    else:
        text = locale.select_deck()
        keyboard = get_deck_list_keyboard(decks, locale)

    if isinstance(event, Message):
        await event.answer(text, reply_markup=keyboard)
    else:
        await event.message.edit_text(text, reply_markup=keyboard)
        await event.answer()


@router.callback_query(F.data.startswith("deck_"))
async def show_deck_actions(callback: CallbackQuery, session: AsyncSession, locale: TranslatorRunner):
    """Show deck actions"""
    deck_id = int(callback.data.split("_")[1])

    deck_repo = DeckRepository(session)
    deck = await deck_repo.get_deck_by_id(deck_id)

    if not deck:
        await callback.answer(locale.deck_not_found(), show_alert=True)
        return

    has_cards = len(deck.cards) > 0
    cards_count = len(deck.cards)

    await callback.message.edit_text(
        locale.deck_info(name=deck.name, count=cards_count),
        reply_markup=get_deck_actions_keyboard(deck_id, has_cards, locale),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("open_deck_"))
async def open_deck(callback: CallbackQuery, session: AsyncSession, locale: TranslatorRunner):
    """Show all cards in deck"""
    deck_id = int(callback.data.split("_")[2])

    card_repo = CardRepository(session)
    cards = await card_repo.get_deck_cards(deck_id)

    if not cards:
        await callback.answer(locale.no_cards(), show_alert=True)
        return

    text = locale.cards_in_deck() + "\n\n"
    for i, card in enumerate(cards, 1):
        text += f"{i}. <b>{locale.question_label()}:</b> {card.question}\n"
        text += f"   <b>{locale.answer_label()}:</b> {card.answer}\n\n"

    await callback.message.edit_text(text, reply_markup=get_deck_actions_keyboard(deck_id, True, locale))
    await callback.answer()


@router.callback_query(F.data.startswith("delete_deck_"))
async def delete_deck_confirm(callback: CallbackQuery, session: AsyncSession, locale: TranslatorRunner):
    """Confirm deck deletion"""
    deck_id = int(callback.data.split("_")[2])

    deck_repo = DeckRepository(session)
    deck = await deck_repo.get_deck_by_id(deck_id)

    if not deck:
        await callback.answer(locale.deck_not_found(), show_alert=True)
        return

    await deck_repo.delete_deck(deck_id)

    await callback.message.edit_text(
        locale.deck_deleted(name=deck.name), reply_markup=get_back_to_menu_keyboard(locale)
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext, locale: TranslatorRunner):
    """Cancel current action"""
    await state.clear()
    await callback.message.edit_text(locale.cancel(), reply_markup=get_back_to_menu_keyboard(locale))
    await callback.answer()

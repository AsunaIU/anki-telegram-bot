from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from memorius.database.repositories import CardRepository, DeckRepository
from memorius.keyboards.keyboards import get_cancel_keyboard, get_card_list_keyboard, get_deck_actions_keyboard
from memorius.utils import CreateCard, EditCard

router = Router()


@router.callback_query(F.data.startswith("add_card_"))
async def add_card_start(callback: CallbackQuery, state: FSMContext, locale: TranslatorRunner):
    """Start adding card"""
    deck_id = int(callback.data.split("_")[2])

    await state.update_data(deck_id=deck_id)
    await state.set_state(CreateCard.waiting_for_question)

    await callback.message.edit_text(locale.enter_question(), reply_markup=get_cancel_keyboard(locale))
    await callback.answer()


@router.message(CreateCard.waiting_for_question)
async def add_card_question(message: Message, state: FSMContext, locale: TranslatorRunner):
    """Process card question"""
    await state.update_data(question=message.text)
    await state.set_state(CreateCard.waiting_for_answer)

    await message.answer(locale.enter_answer(), reply_markup=get_cancel_keyboard(locale))


@router.message(CreateCard.waiting_for_answer)
async def add_card_finish(message: Message, state: FSMContext, session: AsyncSession, locale: TranslatorRunner):
    """Finish adding card"""
    data = await state.get_data()
    deck_id = data["deck_id"]
    question = data["question"]
    answer = message.text

    card_repo = CardRepository(session)
    await card_repo.create_card(deck_id=deck_id, question=question, answer=answer)

    await state.clear()

    deck_repo = DeckRepository(session)
    deck = await deck_repo.get_deck_by_id(deck_id)
    has_cards = len(deck.cards) > 0

    await message.answer(locale.card_added(), reply_markup=get_deck_actions_keyboard(deck_id, has_cards, locale))


@router.callback_query(F.data.startswith("edit_card_"))
async def edit_card_select(callback: CallbackQuery, session: AsyncSession, locale: TranslatorRunner):
    """Select card to edit"""
    deck_id = int(callback.data.split("_")[2])

    card_repo = CardRepository(session)
    cards = await card_repo.get_deck_cards(deck_id)

    if not cards:
        await callback.answer(locale.no_cards(), show_alert=True)
        return

    await callback.message.edit_text(
        locale.select_card_edit(), reply_markup=get_card_list_keyboard(cards, "edit", deck_id, locale)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("edit_card_id_"))
async def edit_card_start(callback: CallbackQuery, state: FSMContext, session: AsyncSession, locale: TranslatorRunner):
    """Start editing card"""
    card_id = int(callback.data.split("_")[3])

    card_repo = CardRepository(session)
    card = await card_repo.get_card_by_id(card_id)

    if not card:
        await callback.answer(locale.card_not_found(), show_alert=True)
        return

    await state.update_data(card_id=card_id, deck_id=card.deck_id)
    await state.set_state(EditCard.waiting_for_new_question)

    await callback.message.edit_text(
        locale.current_question(question=card.question), reply_markup=get_cancel_keyboard(locale)
    )
    await callback.answer()


@router.message(EditCard.waiting_for_new_question)
async def edit_card_question(message: Message, state: FSMContext, locale: TranslatorRunner):
    """Process new question"""
    await state.update_data(new_question=message.text)
    await state.set_state(EditCard.waiting_for_new_answer)

    await message.answer(locale.enter_new_answer(), reply_markup=get_cancel_keyboard(locale))


@router.message(EditCard.waiting_for_new_answer)
async def edit_card_finish(message: Message, state: FSMContext, session: AsyncSession, locale: TranslatorRunner):
    """Finish editing card"""
    data = await state.get_data()
    card_id = data["card_id"]
    deck_id = data["deck_id"]
    new_question = data["new_question"]
    new_answer = message.text

    card_repo = CardRepository(session)
    await card_repo.update_card(card_id=card_id, question=new_question, answer=new_answer)

    await state.clear()

    deck_repo = DeckRepository(session)
    deck = await deck_repo.get_deck_by_id(deck_id)
    has_cards = len(deck.cards) > 0

    await message.answer(locale.card_updated(), reply_markup=get_deck_actions_keyboard(deck_id, has_cards, locale))


@router.callback_query(F.data.startswith("delete_card_"))
async def delete_card_select(callback: CallbackQuery, session: AsyncSession, locale: TranslatorRunner):
    """Select card to delete"""
    deck_id = int(callback.data.split("_")[2])

    card_repo = CardRepository(session)
    cards = await card_repo.get_deck_cards(deck_id)

    if not cards:
        await callback.answer(locale.no_cards(), show_alert=True)
        return

    await callback.message.edit_text(
        locale.select_card_delete(), reply_markup=get_card_list_keyboard(cards, "delete", deck_id, locale)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("delete_card_id_"))
async def delete_card_confirm(callback: CallbackQuery, session: AsyncSession, locale: TranslatorRunner):
    """Confirm card deletion"""
    card_id = int(callback.data.split("_")[3])

    card_repo = CardRepository(session)
    card = await card_repo.get_card_by_id(card_id)

    if not card:
        await callback.answer(locale.card_not_found(), show_alert=True)
        return

    deck_id = card.deck_id
    await card_repo.delete_card(card_id)

    deck_repo = DeckRepository(session)
    deck = await deck_repo.get_deck_by_id(deck_id)
    has_cards = len(deck.cards) > 0

    await callback.message.edit_text(
        locale.card_deleted(), reply_markup=get_deck_actions_keyboard(deck_id, has_cards, locale)
    )
    await callback.answer()

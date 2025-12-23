from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from memorius.database.repositories import CardRepository, DeckRepository, StatisticsRepository
from memorius.keyboards.keyboards import (
    get_deck_actions_keyboard,
    get_difficulty_keyboard,
    get_review_keyboard,
    get_variant_keyboard,
)
from memorius.utils import ReviewSession

router = Router()


@router.callback_query(F.data.startswith("start_session_"))
async def start_session(callback: CallbackQuery, state: FSMContext, session: AsyncSession, locale: TranslatorRunner):
    """Start review session"""
    deck_id = int(callback.data.split("_")[2])

    card_repo = CardRepository(session)
    cards = await card_repo.get_cards_for_review(deck_id)

    if not cards:
        await callback.answer(locale.all_cards_reviewed(), show_alert=True)
        return

    await state.set_state(ReviewSession.in_session)
    await state.update_data(
        deck_id=deck_id, cards=[card.id for card in cards], current_index=0, easy=0, medium=0, hard=0, skipped=0
    )

    card = cards[0]

    if card.card_type == "variants":
        variants_text = ""
        for i in range(1, 5):
            variant = getattr(card, f"variant_{i}", None)
            if variant:
                variants_text += f"{i}. {variant}\n"

        await callback.message.edit_text(
            locale.question_number(current=1, total=len(cards)) + "\n\n" + card.question + "\n\n" + variants_text,
            reply_markup=get_variant_keyboard(card, locale),
        )
    else:
        await callback.message.edit_text(
            locale.question_number(current=1, total=len(cards)) + "\n\n" + card.question,
            reply_markup=get_review_keyboard(locale),
        )

    await callback.answer()


@router.callback_query(F.data == "show_answer", ReviewSession.in_session)
async def show_answer(callback: CallbackQuery, state: FSMContext, session: AsyncSession, locale: TranslatorRunner):
    """Show answer to current card"""
    data = await state.get_data()
    cards = data["cards"]
    current_index = data["current_index"]

    card_repo = CardRepository(session)
    card = await card_repo.get_card_by_id(cards[current_index])

    if not card:
        await callback.answer(locale.card_load_error(), show_alert=True)
        return

    await callback.message.edit_text(
        locale.show_answer_text(question=card.question, answer=card.answer),
        reply_markup=get_difficulty_keyboard(locale),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("variant_answer_"), ReviewSession.in_session)
async def check_variant_answer(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, locale: TranslatorRunner
):
    """Check variant answer"""
    selected_variant = int(callback.data.split("_")[2])

    data = await state.get_data()
    cards = data["cards"]
    current_index = data["current_index"]
    deck_id = data["deck_id"]

    card_repo = CardRepository(session)
    card = await card_repo.get_card_by_id(cards[current_index])

    if not card:
        await callback.answer(locale.card_load_error(), show_alert=True)
        return

    is_correct = selected_variant == card.correct_variant

    difficulty = "easy" if is_correct else "hard"

    await card_repo.update_card_review(card_id=card.id, difficulty=difficulty)

    stats_repo = StatisticsRepository(session)
    await stats_repo.add_statistics(
        user_id=callback.from_user.id, deck_id=deck_id, card_id=card.id, difficulty=difficulty
    )

    await state.update_data(**{difficulty: data[difficulty] + 1})

    result_text = locale.correct_answer() if is_correct else locale.wrong_answer(correct=card.answer)
    await callback.answer(result_text, show_alert=True)

    await next_card(callback, state, session, locale)


@router.callback_query(F.data == "skip_card", ReviewSession.in_session)
async def skip_card(callback: CallbackQuery, state: FSMContext, session: AsyncSession, locale: TranslatorRunner):
    """Skip current card"""
    data = await state.get_data()
    current_index = data["current_index"]
    cards = data["cards"]
    deck_id = data["deck_id"]

    stats_repo = StatisticsRepository(session)
    await stats_repo.add_statistics(
        user_id=callback.from_user.id, deck_id=deck_id, card_id=cards[current_index], difficulty="skipped"
    )

    await state.update_data(skipped=data["skipped"] + 1)

    await next_card(callback, state, session, locale)


@router.callback_query(F.data.startswith("difficulty_"), ReviewSession.in_session)
async def rate_difficulty(callback: CallbackQuery, state: FSMContext, session: AsyncSession, locale: TranslatorRunner):
    """Rate answer difficulty"""
    difficulty = callback.data.split("_")[1]  # easy, medium, hard

    data = await state.get_data()
    current_index = data["current_index"]
    cards = data["cards"]
    deck_id = data["deck_id"]

    card_repo = CardRepository(session)
    await card_repo.update_card_review(card_id=cards[current_index], difficulty=difficulty)

    stats_repo = StatisticsRepository(session)
    await stats_repo.add_statistics(
        user_id=callback.from_user.id, deck_id=deck_id, card_id=cards[current_index], difficulty=difficulty
    )

    await state.update_data(**{difficulty: data[difficulty] + 1})

    await next_card(callback, state, session, locale)


async def next_card(callback: CallbackQuery, state: FSMContext, session: AsyncSession, locale: TranslatorRunner):
    """Move to next card or finish session"""
    data = await state.get_data()
    current_index = data["current_index"] + 1
    cards = data["cards"]
    deck_id = data["deck_id"]

    if current_index >= len(cards):
        total = len(cards)
        easy = data["easy"]
        medium = data["medium"]
        hard = data["hard"]
        skipped = data["skipped"]

        await state.clear()

        deck_repo = DeckRepository(session)
        deck = await deck_repo.get_deck_by_id(deck_id)
        has_cards = len(deck.cards) > 0

        await callback.message.edit_text(
            locale.session_complete(total=total, easy=easy, medium=medium, hard=hard, skipped=skipped),
            reply_markup=get_deck_actions_keyboard(deck_id, has_cards, locale),
        )
    else:
        await state.update_data(current_index=current_index)

        card_repo = CardRepository(session)
        card = await card_repo.get_card_by_id(cards[current_index])

        if card.card_type == "variants":
            variants_text = ""
            for i in range(1, 5):
                variant = getattr(card, f"variant_{i}", None)
                if variant:
                    variants_text += f"{i}. {variant}\n"

            await callback.message.edit_text(
                locale.question_number(current=current_index + 1, total=len(cards))
                + "\n\n"
                + card.question
                + "\n\n"
                + variants_text,
                reply_markup=get_variant_keyboard(card, locale),
            )
        else:
            await callback.message.edit_text(
                locale.question_number(current=current_index + 1, total=len(cards)) + "\n\n" + card.question,
                reply_markup=get_review_keyboard(locale),
            )

    await callback.answer()

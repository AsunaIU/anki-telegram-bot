import asyncio
from contextlib import suppress

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from memorius.config import settings
from memorius.database.repositories import CardRepository, DeckRepository, StatisticsRepository
from memorius.keyboards import (
    get_deck_actions_keyboard,
    get_difficulty_keyboard,
    get_review_keyboard,
    get_variant_keyboard,
)
from memorius.utils import ReviewSession

router = Router()

timeout_tasks = {}


async def handle_timeout(
    user_id: int,
    chat_id: int,
    message_id: int,
    state: FSMContext,
    session: AsyncSession,
    locale: TranslatorRunner,
    bot: Bot,
):
    """Handle question timeout"""
    try:
        await asyncio.sleep(settings.TIMEOUT_SECONDS)

        data = await state.get_data()

        current_state = await state.get_state()
        if current_state != ReviewSession.in_session:
            return

        if not data or "current_index" not in data:
            return

        current_index = data["current_index"]
        cards = data["cards"]
        deck_id = data["deck_id"]

        card_repo = CardRepository(session)
        await card_repo.update_card_review(card_id=cards[current_index], difficulty="hard")

        stats_repo = StatisticsRepository(session)
        await stats_repo.add_statistics(
            user_id=user_id, deck_id=deck_id, card_id=cards[current_index], difficulty="hard"
        )

        hard_count = data.get("hard", 0) + 1
        await state.update_data(hard=hard_count)

        try:
            timeout_msg = locale.timeout_msg()
            await bot.send_message(chat_id=chat_id, text=timeout_msg)
        except suppress(Exception):
            pass

        data = await state.get_data()  # Refresh data
        current_index = data["current_index"] + 1
        cards = data["cards"]
        deck_id = data["deck_id"]

        if current_index >= len(cards):
            total = len(cards)
            easy = data.get("easy", 0)
            medium = data.get("medium", 0)
            hard = data.get("hard", 0)
            skipped = data.get("skipped", 0)

            await state.clear()

            deck_repo = DeckRepository(session)
            deck = await deck_repo.get_deck_by_id(deck_id)
            has_cards = len(deck.cards) > 0

            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=locale.session_complete(total=total, easy=easy, medium=medium, hard=hard, skipped=skipped),
                    reply_markup=get_deck_actions_keyboard(deck_id, has_cards, locale),
                )
            except suppress(Exception):
                pass
        else:
            await state.update_data(current_index=current_index)

            card_repo = CardRepository(session)
            card = await card_repo.get_card_by_id(cards[current_index])

            if card:
                if card.card_type == "variants":
                    variants_text = ""
                    for i in range(1, 5):
                        variant = getattr(card, f"variant_{i}", None)
                        if variant:
                            variants_text += f"{i}. {variant}\n"

                    text = (
                        locale.question_number(current=current_index + 1, total=len(cards))
                        + "\n\n"
                        + card.question
                        + "\n\n"
                        + variants_text
                    )
                    keyboard = get_variant_keyboard(card, locale)
                else:
                    text = locale.question_number(current=current_index + 1, total=len(cards)) + "\n\n" + card.question
                    keyboard = get_review_keyboard(locale)

                try:
                    await bot.edit_message_text(
                        chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard
                    )

                    await start_timeout(user_id, chat_id, message_id, state, session, locale, bot)
                except suppress(Exception):
                    pass

        if user_id in timeout_tasks:
            del timeout_tasks[user_id]

    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error in timeout handler: {e}")


async def start_timeout(
    user_id: int,
    chat_id: int,
    message_id: int,
    state: FSMContext,
    session: AsyncSession,
    locale: TranslatorRunner,
    bot: Bot,
):
    """Start timeout countdown"""
    if user_id in timeout_tasks:
        timeout_tasks[user_id].cancel()

    task = asyncio.create_task(handle_timeout(user_id, chat_id, message_id, state, session, locale, bot))
    timeout_tasks[user_id] = task


def cancel_timeout(user_id: int):
    """Cancel timeout for user"""
    if user_id in timeout_tasks:
        timeout_tasks[user_id].cancel()
        del timeout_tasks[user_id]


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

    await start_timeout(
        callback.from_user.id,
        callback.message.chat.id,
        callback.message.message_id,
        state,
        session,
        locale,
        callback.bot,
    )


@router.callback_query(F.data == "show_answer", ReviewSession.in_session)
async def show_answer(callback: CallbackQuery, state: FSMContext, session: AsyncSession, locale: TranslatorRunner):
    """Show answer to current card"""
    cancel_timeout(callback.from_user.id)

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

    await start_timeout(
        callback.from_user.id,
        callback.message.chat.id,
        callback.message.message_id,
        state,
        session,
        locale,
        callback.bot,
    )


@router.callback_query(F.data.startswith("variant_answer_"), ReviewSession.in_session)
async def check_variant_answer(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, locale: TranslatorRunner
):
    """Check variant answer"""
    cancel_timeout(callback.from_user.id)

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
    cancel_timeout(callback.from_user.id)

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
    cancel_timeout(callback.from_user.id)

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
        cancel_timeout(callback.from_user.id)

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

        await start_timeout(
            callback.from_user.id,
            callback.message.chat.id,
            callback.message.message_id,
            state,
            session,
            locale,
            callback.bot,
        )

    await callback.answer()

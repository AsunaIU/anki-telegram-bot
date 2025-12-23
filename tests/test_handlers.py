from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Chat, InlineKeyboardMarkup, Message, User
from sqlalchemy.ext.asyncio import AsyncSession

from memorius.handlers.user.card import (
    add_card_correct_variant,
    add_card_finish,
    add_card_question,
    add_card_start,
    add_card_type_selected,
    add_card_variants,
)
from memorius.handlers.user.deck import (
    create_deck_finish,
    create_deck_start,
    show_deck_actions,
    show_my_decks,
)
from memorius.handlers.user.session import (
    check_variant_answer,
    rate_difficulty,
    show_answer,
    skip_card,
    start_session,
)
from memorius.utils import CreateCard, CreateDeck, ReviewSession


@pytest.fixture
def mock_user():
    """Create mock user"""
    user = MagicMock(spec=User)
    user.id = 123456789
    user.username = "testuser"
    user.first_name = "Test"
    user.last_name = "User"
    return user


@pytest.fixture
def mock_chat():
    """Create mock chat"""
    chat = MagicMock(spec=Chat)
    chat.id = 123456789
    return chat


@pytest.fixture
def mock_message(mock_user, mock_chat):
    """Create mock message"""
    message = MagicMock(spec=Message)
    message.from_user = mock_user
    message.chat = mock_chat
    message.text = "Test message"
    message.message_id = 1
    message.answer = AsyncMock()
    message.edit_text = AsyncMock()
    message.delete = AsyncMock()
    return message


@pytest.fixture
def mock_callback(mock_user, mock_message):
    """Create mock callback query"""
    callback = MagicMock(spec=CallbackQuery)
    callback.from_user = mock_user
    callback.message = mock_message
    callback.data = "test_data"
    callback.bot = AsyncMock()
    callback.answer = AsyncMock()
    return callback


@pytest.fixture
def mock_state():
    """Create mock FSM state"""
    state = AsyncMock(spec=FSMContext)
    state.get_data = AsyncMock(return_value={})
    state.update_data = AsyncMock()
    state.set_state = AsyncMock()
    state.clear = AsyncMock()
    state.get_state = AsyncMock(return_value=None)
    return state


@pytest.fixture
def mock_session():
    """Create mock database session"""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_locale():
    """Create mock translator"""
    locale = MagicMock()
    locale.select_card_type = MagicMock(return_value="Select card type")
    locale.enter_question = MagicMock(return_value="Enter question")
    locale.enter_answer = MagicMock(return_value="Enter answer")
    locale.enter_variants = MagicMock(return_value="Enter variants")
    locale.card_added = MagicMock(return_value="Card added")
    locale.card_updated = MagicMock(return_value="Card updated")
    locale.variants_count_error = MagicMock(return_value="Variants count error")
    locale.select_correct_variant = MagicMock(return_value="Select correct variant")
    locale.invalid_variant_number = MagicMock(return_value="Invalid variant number")
    locale.enter_number_only = MagicMock(return_value="Enter number only")
    locale.enter_deck_name = MagicMock(return_value="Enter deck name")
    locale.deck_created = MagicMock(return_value="Deck created")
    locale.deck_invalid_name = MagicMock(return_value="Invalid deck name")
    locale.no_decks = MagicMock(return_value="No decks")
    locale.select_deck = MagicMock(return_value="Select deck")
    locale.deck_info = MagicMock(return_value="Deck info")
    locale.question_number = MagicMock(return_value="Question 1/10")
    locale.show_answer_text = MagicMock(return_value="Answer text")
    locale.correct_answer = MagicMock(return_value="Correct!")
    locale.wrong_answer = MagicMock(return_value="Wrong!")
    locale.session_complete = MagicMock(return_value="Session complete")
    locale.all_cards_reviewed = MagicMock(return_value="All cards reviewed")
    locale.card_load_error = MagicMock(return_value="Card load error")
    return locale


@pytest.fixture
def mock_keyboard():
    """Create mock keyboard"""
    return MagicMock(spec=InlineKeyboardMarkup)


class TestCardHandlers:
    """Tests for card handlers"""

    @pytest.mark.asyncio
    async def test_add_card_start(self, mock_callback, mock_state, mock_locale, mock_keyboard):
        """Test starting card creation"""
        mock_callback.data = "add_card_123"

        with patch("memorius.handlers.user.card.get_card_type_keyboard", return_value=mock_keyboard):
            await add_card_start(mock_callback, mock_state, mock_locale)

            mock_state.update_data.assert_called_once_with(deck_id=123)
            mock_state.set_state.assert_called_once_with(CreateCard.waiting_for_card_type)
            mock_callback.message.edit_text.assert_called_once()
            mock_callback.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_card_type_selected_text(self, mock_callback, mock_state, mock_locale, mock_keyboard):
        """Test selecting text card type"""
        mock_callback.data = "card_type_text"

        with patch("memorius.handlers.user.card.get_cancel_keyboard", return_value=mock_keyboard):
            await add_card_type_selected(mock_callback, mock_state, mock_locale)

            mock_state.update_data.assert_called_once_with(card_type="text")
            mock_state.set_state.assert_called_once_with(CreateCard.waiting_for_question)
            mock_callback.message.edit_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_card_type_selected_variants(self, mock_callback, mock_state, mock_locale, mock_keyboard):
        """Test selecting variants card type"""
        mock_callback.data = "card_type_variants"

        with patch("memorius.handlers.user.card.get_cancel_keyboard", return_value=mock_keyboard):
            await add_card_type_selected(mock_callback, mock_state, mock_locale)

            mock_state.update_data.assert_called_once_with(card_type="variants")
            mock_state.set_state.assert_called_once_with(CreateCard.waiting_for_question)

    @pytest.mark.asyncio
    async def test_add_card_question_text_type(self, mock_message, mock_state, mock_locale, mock_keyboard):
        """Test adding question for text card"""
        mock_message.text = "What is 2+2?"
        mock_state.get_data = AsyncMock(return_value={"card_type": "text"})

        with patch("memorius.handlers.user.card.get_cancel_keyboard", return_value=mock_keyboard):
            await add_card_question(mock_message, mock_state, mock_locale)

            mock_state.update_data.assert_called_once_with(question="What is 2+2?")
            mock_state.set_state.assert_called_once_with(CreateCard.waiting_for_answer)
            mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_card_question_variants_type(self, mock_message, mock_state, mock_locale, mock_keyboard):
        """Test adding question for variants card"""
        mock_message.text = "What is the capital of France?"
        mock_state.get_data = AsyncMock(return_value={"card_type": "variants"})

        with patch("memorius.handlers.user.card.get_cancel_keyboard", return_value=mock_keyboard):
            await add_card_question(mock_message, mock_state, mock_locale)

            mock_state.update_data.assert_called_once_with(question="What is the capital of France?")
            mock_state.set_state.assert_called_once_with(CreateCard.waiting_for_variants)

    @pytest.mark.asyncio
    async def test_add_card_finish(self, mock_message, mock_state, mock_session, mock_locale, mock_keyboard):
        """Test finishing text card creation"""
        mock_message.text = "4"
        mock_state.get_data = AsyncMock(return_value={"deck_id": 123, "question": "What is 2+2?"})

        with (
            patch("memorius.handlers.user.card.CardRepository") as mock_card_repo_class,
            patch("memorius.handlers.user.card.DeckRepository") as mock_deck_repo_class,
            patch("memorius.handlers.user.card.get_deck_actions_keyboard", return_value=mock_keyboard),
        ):
            # Create mock instances
            mock_card_repo = AsyncMock()
            mock_card_repo.create_card = AsyncMock()
            mock_card_repo_class.return_value = mock_card_repo

            mock_deck = MagicMock()
            mock_deck.cards = [MagicMock()]

            mock_deck_repo = AsyncMock()
            mock_deck_repo.get_deck_by_id = AsyncMock(return_value=mock_deck)
            mock_deck_repo_class.return_value = mock_deck_repo

            await add_card_finish(mock_message, mock_state, mock_session, mock_locale)

            mock_card_repo.create_card.assert_called_once()
            mock_state.clear.assert_called_once()
            mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_card_variants_valid(self, mock_message, mock_state, mock_locale, mock_keyboard):
        """Test adding valid variants"""
        mock_message.text = "Paris\nLondon\nBerlin"

        with patch("memorius.handlers.user.card.get_cancel_keyboard", return_value=mock_keyboard):
            await add_card_variants(mock_message, mock_state, mock_locale)

            mock_state.update_data.assert_called_once()
            mock_state.set_state.assert_called_once_with(CreateCard.waiting_for_correct_variant)
            mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_card_variants_too_few(self, mock_message, mock_state, mock_locale, mock_keyboard):
        """Test adding too few variants"""
        mock_message.text = "Paris"

        with patch("memorius.handlers.user.card.get_cancel_keyboard", return_value=mock_keyboard):
            await add_card_variants(mock_message, mock_state, mock_locale)

            mock_state.set_state.assert_not_called()
            mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_card_variants_too_many(self, mock_message, mock_state, mock_locale, mock_keyboard):
        """Test adding too many variants"""
        mock_message.text = "Paris\nLondon\nBerlin\nMadrid\nRome"

        with patch("memorius.handlers.user.card.get_cancel_keyboard", return_value=mock_keyboard):
            await add_card_variants(mock_message, mock_state, mock_locale)

            mock_state.set_state.assert_not_called()
            mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_card_correct_variant_valid(
        self, mock_message, mock_state, mock_session, mock_locale, mock_keyboard
    ):
        """Test selecting valid correct variant"""
        mock_message.text = "1"
        mock_state.get_data = AsyncMock(
            return_value={
                "deck_id": 123,
                "question": "What is the capital?",
                "variant_1": "Paris",
                "variant_2": "London",
                "variant_3": "Berlin",
                "variant_4": None,
            }
        )

        with (
            patch("memorius.handlers.user.card.CardRepository") as mock_card_repo_class,
            patch("memorius.handlers.user.card.DeckRepository") as mock_deck_repo_class,
            patch("memorius.handlers.user.card.get_deck_actions_keyboard", return_value=mock_keyboard),
        ):
            mock_card_repo = AsyncMock()
            mock_card_repo.create_card = AsyncMock()
            mock_card_repo_class.return_value = mock_card_repo

            mock_deck = MagicMock()
            mock_deck.cards = [MagicMock()]

            mock_deck_repo = AsyncMock()
            mock_deck_repo.get_deck_by_id = AsyncMock(return_value=mock_deck)
            mock_deck_repo_class.return_value = mock_deck_repo

            await add_card_correct_variant(mock_message, mock_state, mock_session, mock_locale)

            mock_card_repo.create_card.assert_called_once()
            mock_state.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_card_correct_variant_invalid(
        self, mock_message, mock_state, mock_session, mock_locale, mock_keyboard
    ):
        """Test selecting invalid correct variant"""
        mock_message.text = "5"
        mock_state.get_data = AsyncMock(
            return_value={
                "deck_id": 123,
                "question": "What is the capital?",
                "variant_1": "Paris",
                "variant_2": "London",
                "variant_3": None,
                "variant_4": None,
            }
        )

        with patch("memorius.handlers.user.card.get_cancel_keyboard", return_value=mock_keyboard):
            await add_card_correct_variant(mock_message, mock_state, mock_session, mock_locale)

            mock_state.clear.assert_not_called()
            mock_message.answer.assert_called_once()


class TestDeckHandlers:
    """Tests for deck handlers"""

    @pytest.mark.asyncio
    async def test_create_deck_start(self, mock_message, mock_state, mock_locale, mock_keyboard):
        """Test starting deck creation"""
        with patch("memorius.handlers.user.deck.get_cancel_keyboard", return_value=mock_keyboard):
            await create_deck_start(mock_message, mock_state, mock_locale)

            mock_state.set_state.assert_called_once_with(CreateDeck.waiting_for_name)
            mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_deck_finish_valid_name(
        self, mock_message, mock_state, mock_session, mock_locale, mock_keyboard
    ):
        """Test finishing deck creation with valid name"""
        mock_message.text = "My Test Deck"

        with (
            patch("memorius.handlers.user.deck.validate_deck_name", return_value=True),
            patch("memorius.handlers.user.deck.DeckRepository") as mock_deck_repo_class,
            patch("memorius.handlers.user.deck.get_after_create_deck_keyboard", return_value=mock_keyboard),
        ):
            mock_deck = MagicMock()
            mock_deck.id = 456

            mock_deck_repo = AsyncMock()
            mock_deck_repo.create_deck = AsyncMock(return_value=mock_deck)
            mock_deck_repo_class.return_value = mock_deck_repo

            await create_deck_finish(mock_message, mock_state, mock_session, mock_locale)

            mock_deck_repo.create_deck.assert_called_once()
            mock_state.clear.assert_called_once()
            mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_deck_finish_invalid_name(
        self, mock_message, mock_state, mock_session, mock_locale, mock_keyboard
    ):
        """Test finishing deck creation with invalid name"""
        mock_message.text = ""

        with (
            patch("memorius.handlers.user.deck.validate_deck_name", return_value=False),
            patch("memorius.handlers.user.deck.get_cancel_keyboard", return_value=mock_keyboard),
        ):
            await create_deck_finish(mock_message, mock_state, mock_session, mock_locale)

            mock_state.clear.assert_not_called()
            mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_show_my_decks_with_decks(self, mock_message, mock_session, mock_locale, mock_keyboard):
        """Test showing decks when user has decks"""
        with (
            patch("memorius.handlers.user.deck.DeckRepository") as mock_deck_repo_class,
            patch("memorius.handlers.user.deck.get_deck_list_keyboard", return_value=mock_keyboard),
        ):
            mock_deck_repo = AsyncMock()
            mock_deck_repo.get_user_decks = AsyncMock(
                return_value=[MagicMock(id=1, name="Deck 1"), MagicMock(id=2, name="Deck 2")]
            )
            mock_deck_repo_class.return_value = mock_deck_repo

            await show_my_decks(mock_message, mock_session, mock_locale)

            mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_show_my_decks_no_decks(self, mock_message, mock_session, mock_locale, mock_keyboard):
        """Test showing decks when user has no decks"""
        with (
            patch("memorius.handlers.user.deck.DeckRepository") as mock_deck_repo_class,
            patch("memorius.handlers.user.deck.get_back_to_menu_keyboard", return_value=mock_keyboard),
        ):
            mock_deck_repo = AsyncMock()
            mock_deck_repo.get_user_decks = AsyncMock(return_value=[])
            mock_deck_repo_class.return_value = mock_deck_repo

            await show_my_decks(mock_message, mock_session, mock_locale)

            mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_show_deck_actions(self, mock_callback, mock_session, mock_locale, mock_keyboard):
        """Test showing deck actions"""
        mock_callback.data = "deck_123"

        with (
            patch("memorius.handlers.user.deck.DeckRepository") as mock_deck_repo_class,
            patch("memorius.handlers.user.deck.get_deck_actions_keyboard", return_value=mock_keyboard),
        ):
            mock_deck = MagicMock()
            mock_deck.name = "Test Deck"
            mock_deck.cards = [MagicMock(), MagicMock()]

            mock_deck_repo = AsyncMock()
            mock_deck_repo.get_deck_by_id = AsyncMock(return_value=mock_deck)
            mock_deck_repo_class.return_value = mock_deck_repo

            await show_deck_actions(mock_callback, mock_session, mock_locale)

            mock_callback.message.edit_text.assert_called_once()
            mock_callback.answer.assert_called_once()


class TestSessionHandlers:
    """Tests for review session handlers"""

    @pytest.mark.asyncio
    async def test_start_session_with_cards(self, mock_callback, mock_state, mock_session, mock_locale, mock_keyboard):
        """Test starting review session with available cards"""
        mock_callback.data = "start_session_123"

        with (
            patch("memorius.handlers.user.session.CardRepository") as mock_card_repo_class,
            patch("memorius.handlers.user.session.start_timeout") as mock_timeout,
            patch("memorius.handlers.user.session.get_review_keyboard", return_value=mock_keyboard),
        ):
            mock_card = MagicMock()
            mock_card.id = 1
            mock_card.card_type = "text"
            mock_card.question = "Test question"

            mock_card_repo = AsyncMock()
            mock_card_repo.get_cards_for_review = AsyncMock(return_value=[mock_card])
            mock_card_repo_class.return_value = mock_card_repo

            await start_session(mock_callback, mock_state, mock_session, mock_locale)

            mock_state.set_state.assert_called_once_with(ReviewSession.in_session)
            mock_state.update_data.assert_called_once()
            mock_callback.message.edit_text.assert_called_once()
            mock_timeout.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_session_no_cards(self, mock_callback, mock_state, mock_session, mock_locale):
        """Test starting review session with no available cards"""
        mock_callback.data = "start_session_123"

        with patch("memorius.handlers.user.session.CardRepository") as mock_card_repo_class:
            mock_card_repo = AsyncMock()
            mock_card_repo.get_cards_for_review = AsyncMock(return_value=[])
            mock_card_repo_class.return_value = mock_card_repo

            await start_session(mock_callback, mock_state, mock_session, mock_locale)

            mock_state.set_state.assert_not_called()
            mock_callback.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_show_answer(self, mock_callback, mock_state, mock_session, mock_locale, mock_keyboard):
        """Test showing answer to current card"""
        mock_state.get_data = AsyncMock(return_value={"cards": [1, 2, 3], "current_index": 0})

        with (
            patch("memorius.handlers.user.session.CardRepository") as mock_card_repo_class,
            patch("memorius.handlers.user.session.cancel_timeout") as mock_cancel,
            patch("memorius.handlers.user.session.start_timeout") as mock_timeout,
            patch("memorius.handlers.user.session.get_difficulty_keyboard", return_value=mock_keyboard),
        ):
            mock_card = MagicMock()
            mock_card.question = "Test question"
            mock_card.answer = "Test answer"

            mock_card_repo = AsyncMock()
            mock_card_repo.get_card_by_id = AsyncMock(return_value=mock_card)
            mock_card_repo_class.return_value = mock_card_repo

            await show_answer(mock_callback, mock_state, mock_session, mock_locale)

            mock_cancel.assert_called_once()
            mock_callback.message.edit_text.assert_called_once()
            mock_timeout.assert_called_once()

    @pytest.mark.asyncio
    async def test_skip_card(self, mock_callback, mock_state, mock_session, mock_locale):
        """Test skipping a card"""
        mock_state.get_data = AsyncMock(
            return_value={
                "cards": [1, 2, 3],
                "current_index": 0,
                "deck_id": 123,
                "skipped": 0,
                "easy": 0,
                "medium": 0,
                "hard": 0,
            }
        )

        with (
            patch("memorius.handlers.user.session.StatisticsRepository") as mock_stats_repo_class,
            patch("memorius.handlers.user.session.cancel_timeout") as mock_cancel,
            patch("memorius.handlers.user.session.next_card") as mock_next,
        ):
            mock_stats_repo = AsyncMock()
            mock_stats_repo.add_statistics = AsyncMock()
            mock_stats_repo_class.return_value = mock_stats_repo

            await skip_card(mock_callback, mock_state, mock_session, mock_locale)

            mock_cancel.assert_called_once()
            mock_stats_repo.add_statistics.assert_called_once()
            mock_state.update_data.assert_called_once()
            mock_next.assert_called_once()

    @pytest.mark.asyncio
    async def test_rate_difficulty(self, mock_callback, mock_state, mock_session, mock_locale):
        """Test rating answer difficulty"""
        mock_callback.data = "difficulty_easy"
        mock_state.get_data = AsyncMock(
            return_value={"cards": [1, 2, 3], "current_index": 0, "deck_id": 123, "easy": 0, "medium": 0, "hard": 0}
        )

        with (
            patch("memorius.handlers.user.session.CardRepository") as mock_card_repo_class,
            patch("memorius.handlers.user.session.StatisticsRepository") as mock_stats_repo_class,
            patch("memorius.handlers.user.session.cancel_timeout") as mock_cancel,
            patch("memorius.handlers.user.session.next_card") as mock_next,
        ):
            mock_card_repo = AsyncMock()
            mock_card_repo.update_card_review = AsyncMock()
            mock_card_repo_class.return_value = mock_card_repo

            mock_stats_repo = AsyncMock()
            mock_stats_repo.add_statistics = AsyncMock()
            mock_stats_repo_class.return_value = mock_stats_repo

            await rate_difficulty(mock_callback, mock_state, mock_session, mock_locale)

            mock_cancel.assert_called_once()
            mock_card_repo.update_card_review.assert_called_once()
            mock_stats_repo.add_statistics.assert_called_once()
            mock_next.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_variant_answer_correct(self, mock_callback, mock_state, mock_session, mock_locale):
        """Test checking correct variant answer"""
        mock_callback.data = "variant_answer_1"
        mock_state.get_data = AsyncMock(
            return_value={"cards": [1, 2, 3], "current_index": 0, "deck_id": 123, "easy": 0, "medium": 0, "hard": 0}
        )

        with (
            patch("memorius.handlers.user.session.CardRepository") as mock_card_repo_class,
            patch("memorius.handlers.user.session.StatisticsRepository") as mock_stats_repo_class,
            patch("memorius.handlers.user.session.cancel_timeout") as mock_cancel,
            patch("memorius.handlers.user.session.next_card") as mock_next,
        ):
            mock_card = MagicMock()
            mock_card.id = 1
            mock_card.correct_variant = 1
            mock_card.answer = "Correct Answer"

            mock_card_repo = AsyncMock()
            mock_card_repo.get_card_by_id = AsyncMock(return_value=mock_card)
            mock_card_repo.update_card_review = AsyncMock()
            mock_card_repo_class.return_value = mock_card_repo

            mock_stats_repo = AsyncMock()
            mock_stats_repo.add_statistics = AsyncMock()
            mock_stats_repo_class.return_value = mock_stats_repo

            await check_variant_answer(mock_callback, mock_state, mock_session, mock_locale)

            mock_cancel.assert_called_once()
            mock_card_repo.update_card_review.assert_called_once()
            mock_stats_repo.add_statistics.assert_called_once()
            mock_next.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

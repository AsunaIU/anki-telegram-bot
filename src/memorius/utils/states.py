from aiogram.fsm.state import State, StatesGroup


class CreateDeck(StatesGroup):
    """States for creating deck"""

    waiting_for_name = State()


class CreateCard(StatesGroup):
    """States for creating card"""

    waiting_for_question = State()
    waiting_for_answer = State()


class EditCard(StatesGroup):
    """States for editing card"""

    waiting_for_new_question = State()
    waiting_for_new_answer = State()


class ReviewSession(StatesGroup):
    """States for review session"""

    in_session = State()

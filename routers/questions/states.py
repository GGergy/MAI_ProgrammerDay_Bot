from aiogram.fsm.state import StatesGroup, State


class QuestionStates(StatesGroup):
    category = State()
    difficulty = State()
    question = State()

from aiogram.fsm.state import StatesGroup, State


class RegisterStates(StatesGroup):
    username = State()
    faculty = State()

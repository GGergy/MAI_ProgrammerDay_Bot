from aiogram.filters.callback_data import CallbackData


class GiveAnswer(CallbackData, prefix="give_answer"):
    answer_id: int

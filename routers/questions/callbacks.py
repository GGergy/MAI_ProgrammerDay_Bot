from aiogram.filters.callback_data import CallbackData

class ReceiveQuestion(CallbackData, prefix="receive_question"):
    ...


class SelectCategory(CallbackData, prefix="select_category"):
    ...


class SelectDifficulty(CallbackData, prefix="select_category"):
    ...
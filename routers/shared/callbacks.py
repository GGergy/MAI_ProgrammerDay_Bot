from aiogram.filters.callback_data import CallbackData


class DeleteCallback(CallbackData, prefix="del"):
    ...


class MenuCallback(CallbackData, prefix="menu"):
    ...
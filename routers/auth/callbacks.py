from aiogram.filters.callback_data import CallbackData


class ConfirmProfileReg(CallbackData, prefix="reg_confirm"):
    ...


class RecreateProfileReg(CallbackData, prefix="reg_recreate"):
    ...

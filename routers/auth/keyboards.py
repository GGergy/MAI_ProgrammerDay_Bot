from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from routers.auth import callbacks


confirmation_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data=callbacks.ConfirmProfileReg().pack())],
        [InlineKeyboardButton(text="🔄 Заполнить заново", callback_data=callbacks.RecreateProfileReg().pack())]
    ],
    resize_keyboard=True
)


refresh_stats_button = InlineKeyboardButton(text="🔄 Обновить статистику", callback_data=callbacks.RefreshStats().pack())
frozen_refresh_stats_button = InlineKeyboardButton(text="🔄 Обновить статистику", callback_data=callbacks.RefreshStats(deletable=False).pack())
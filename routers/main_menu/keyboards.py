from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from routers.main_menu import callbacks


main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Играть 🚀", callback_data=callbacks.ReceiveQuestion().pack())],
        [InlineKeyboardButton(text="👮‍♂️ Профиль 👮‍♀️", callback_data=callbacks.CheckProfile().pack())],
        [InlineKeyboardButton(text="🎖 Таблица лидеров 🎖", callback_data=callbacks.CheckLadder().pack())],
        [InlineKeyboardButton(text="🔐 Призы 🔓", callback_data=callbacks.CheckPrizes().pack())],
    ],
    resize_keyboard=True
)
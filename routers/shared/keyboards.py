from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from routers.shared.callbacks import DeleteCallback


delete_button = InlineKeyboardButton(text="❌Закрыть", callback_data=DeleteCallback().pack())
delete_markup = InlineKeyboardMarkup(inline_keyboard=[[delete_button]])
# Логика делита не прописана!!!
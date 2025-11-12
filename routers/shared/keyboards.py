from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from routers.shared.callbacks import DeleteCallback, MenuCallback


delete_button = InlineKeyboardButton(text="❌Закрыть", callback_data=DeleteCallback().pack())
delete_markup = InlineKeyboardMarkup(inline_keyboard=[[delete_button]])
menu_button = InlineKeyboardButton(text="В главное меню", callback_data=MenuCallback().pack())
menu_markup = InlineKeyboardMarkup(inline_keyboard=[[menu_button]])
# Логика делита не прописана!!!
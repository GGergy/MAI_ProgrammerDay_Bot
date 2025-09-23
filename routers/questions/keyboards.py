from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from routers.questions import callbacks
from utils.models import conn, Category, User


def gen_cat_markup():
    categories = ("Категория 1", "Категория 2", "Категория 3", ) #TODO Клавиатура должна генерироваться динамически
    category_buttons = []
    for i, cat in enumerate(categories):
        category_buttons.append([InlineKeyboardButton(text=cat, callback_data=callbacks.SelectCategory().pack())])
    
    cat_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            *category_buttons
        ],
        resize_keyboard=True
    )
    return cat_markup


def gen_difficulty_markup():
    difficulties = ("Легко 1⭐️", "Нормально 2⭐️", "Сложно 4⭐️", ) #TODO Клавиатура должна генерироваться динамически
    diff_buttons = []
    for i, diff in enumerate(difficulties):
        diff_buttons.append([InlineKeyboardButton(text=diff, callback_data=callbacks.SelectDifficulty().pack())])
    
    diff_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            *diff_buttons
        ],
        resize_keyboard=True
    )
    return diff_markup
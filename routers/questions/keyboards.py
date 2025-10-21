import math

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from routers.questions.callbacks import GiveAnswer
from utils.models import AnswerOption


def gen_question_kb(answers: list[AnswerOption]) -> InlineKeyboardMarkup:
    mk = InlineKeyboardMarkup(inline_keyboard=[])
    row_size = math.ceil(len(answers) ** 0.5)
    for i in range(0, len(answers), row_size):
        mk.inline_keyboard.append([
            InlineKeyboardButton(text=f"№{j + 1}", callback_data=GiveAnswer(answer_id=answers[j].id).pack())
            for j in range(i, min(i + row_size, len(answers)))
        ])
    return mk


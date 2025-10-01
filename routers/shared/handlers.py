import asyncio
import re
from datetime import datetime, timedelta

from aiogram import types, Router
from aiogram.fsm.context import FSMContext

from routers.auth.states import RegisterStates
from routers.shared.callbacks import DeleteCallback, MenuCallback
from routers.main_menu.keyboards import main_menu_keyboard

from utils.models import conn, User, Pending, Question
from utils.templateutil import render
from utils.config import settings

router = Router(name=__name__)


def normalize_text(text: str) -> str:
    text = text.lower()
    re.sub(r"\w", "", text)
    return text


async def scheduler():
    while True:
        await asyncio.sleep(settings.answer_timeout / 5)
        ts = datetime.now()
        with conn() as session:
            objects = session.query(Pending).all()
            for obj in objects:
                if ts - obj.created_at >= timedelta(seconds=settings.answer_timeout):
                    question = session.get(Question, obj.question_id)
                    if question.status == Question.QStatuses.PENDING:
                        question.status = Question.QStatuses.OPEN
                    session.delete(obj)
            session.commit()


@router.callback_query(DeleteCallback.filter())
async def close(query: types.CallbackQuery):
    await query.answer()
    if query.message.reply_to_message:
        await query.message.reply_to_message.delete()
    await query.message.delete()


#TODO Повторение логики /start
@router.callback_query(MenuCallback.filter())
async def back_to_menu(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    if query.message.reply_to_message:
        await query.message.reply_to_message.delete()
    with conn() as session:
        user = session.get(User, query.from_user.id)

    await query.message.edit_text(
        text=render("auth/hello.html", user=user),
        reply_markup=main_menu_keyboard,
    )

    if not user:
        await state.set_state(RegisterStates.username)
        await state.update_data(msg_id=query.message.message_id)


# Удаление всех необработанных сообщений, определяется последней
@router.message()
async def deleter(message: types.Message):
    await message.delete()

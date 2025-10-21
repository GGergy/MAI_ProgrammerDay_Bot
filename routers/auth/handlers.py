import aiogram.exceptions
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup

from routers.auth.callbacks import RefreshStats
from routers.auth.keyboards import refresh_stats_button, frozen_refresh_stats_button
from routers.questions.keyboards import gen_question_kb
from routers.questions.states import wait_answer
from routers.shared.keyboards import delete_markup, delete_button
from utils.models import conn, User, QRcode, Question, AnsweredQuestion, Pending
from utils.templateutil import render

router = Router(name=__name__)


@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    with conn() as session:
        user = session.get(User, message.chat.id)
        if not user:
            user = User(telegram_id=message.chat.id, username=message.from_user.username)
            session.add(user)
            session.commit()
            user = session.get(User, message.chat.id)
            await message.answer(text=render("auth/hello.html", user_id=user.telegram_id, founded=0, correct=0),
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[[frozen_refresh_stats_button]]))

    qr_id = message.text.split(" ")[-1]
    if qr_id == "/start":
        await message.answer(text=render("auth/hello.html", user_id=user.telegram_id,
                                         founded=AnsweredQuestion.num_founded_qrs(session, user.telegram_id),
                                         correct=AnsweredQuestion.num_correct_questions(session, user.telegram_id)),
                             reply_markup=InlineKeyboardMarkup(
                                 inline_keyboard=[[refresh_stats_button], [delete_button]]))
        await message.delete()
        return
    if Pending.get_lock(session, user.telegram_id):
        await message.answer(text=render("questions/you_locked.html"), reply_markup=delete_markup)
        await message.delete()
        return
    qr_id = int(qr_id)

    with conn() as session:
        qr = session.get(QRcode, qr_id)
        if not qr:
            await message.answer(text=render("questions/qr_incorrect.html"), reply_markup=delete_markup)
            await message.delete()
            return

        if AnsweredQuestion.get_qr_lock(session, user.telegram_id, qr_id):
            await message.answer(text=render("questions/already_answered.html"), reply_markup=delete_markup)
            await message.delete()
            return
        question = Question.get_open(session, qr_id)
        if not question:
            await message.answer(
                text=render("questions/qr_empty.html", pending_count=Pending.get_num_pending(session, qr_id)),
                reply_markup=delete_markup)
            return

        question.status = Question.QStatuses.PENDING
        locker = Pending(question_id=question.id, user_id=user.telegram_id)
        session.add(locker)
        session.commit()

        if question.type == Question.QTypes.BUTTONS:
            mk = gen_question_kb(question.answers)
            ans_list = [answer.text for answer in question.answers]
        else:
            await state.set_state(wait_answer)
            await state.update_data(question_id=question.id)
            mk = None
            ans_list = []

        msg = await message.answer(text=render("questions/question.html", question=question, answers=ans_list),
                                   reply_markup=mk)
        await state.update_data(msg_id=msg.message_id)
        await message.delete()


@router.callback_query(RefreshStats.filter())
async def refresh_stats(query: types.CallbackQuery, callback_data: RefreshStats):
    uid = query.message.chat.id
    with conn() as session:
        kb = [[refresh_stats_button], [delete_button]] if callback_data.deletable else [[frozen_refresh_stats_button]]
        try:
            await query.message.edit_text(text=render("auth/hello.html", user_id=uid,
                                                      founded=AnsweredQuestion.num_founded_qrs(session, uid),
                                                      correct=AnsweredQuestion.num_correct_questions(session, uid)),
                                          reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
        except aiogram.exceptions.TelegramAPIError:
            await query.answer("Статистика актуальная")

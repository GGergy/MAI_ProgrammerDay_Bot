from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from routers.questions.keyboards import gen_question_kb
from routers.questions.states import wait_answer
from routers.shared.keyboards import delete_markup
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

    qr_id = message.text.split(" ")[-1]
    if qr_id == "/start":
        await message.answer(text=render("auth/hello.html", user=user), reply_markup=delete_markup)
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

        qr_answer = session.query(AnsweredQuestion).filter(
            AnsweredQuestion.user_id == user.telegram_id).join(
            Question, Question.id == AnsweredQuestion.question_id).filter(
            Question.qrcode_id == qr_id).first()
        if qr_answer:
            await message.answer(text=render("questions/already_answered.html"), reply_markup=delete_markup)
            await message.delete()
            return
        question: Question = session.query(Question).filter(
            (Question.qrcode_id == qr_id) & (Question.status == Question.QStatuses.OPEN)).first()
        if not question:
            print(Pending.get_num_pending(session, qr_id))
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
        else:
            await state.set_state(wait_answer)
            await state.update_data(question_id=question.id)
            mk = None
        await message.answer(text=render("questions/question.html", question=question), reply_markup=mk)
        await message.delete()

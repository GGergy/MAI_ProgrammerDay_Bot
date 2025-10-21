from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from routers.questions.callbacks import GiveAnswer
from routers.questions.states import wait_answer
from routers.shared.keyboards import delete_markup
from routers.shared.handlers import normalize_text
from utils.models import conn, AnswerOption, AnsweredQuestion, Question, Pending
from utils.templateutil import render

router = Router(name=__name__)


@router.callback_query(GiveAnswer.filter())
async def handle_button_answer(query: CallbackQuery, callback_data: GiveAnswer):
    with conn() as session:
        answer = session.get(AnswerOption, callback_data.answer_id)

        lock = Pending.get_lock(session, query.message.chat.id)
        if not lock or lock.question_id != answer.question_id:
            await query.message.edit_text(text=render("questions/expired.html"), reply_markup=delete_markup)
            return
        session.delete(lock)
        question = session.get(Question, answer.question_id)
        if answer.correct:
            question.status = Question.QStatuses.CLOSED
        else:
            question.status = Question.QStatuses.OPEN

        answered_q = AnsweredQuestion(answer_id=answer.id, question_id=answer.question_id,
                                      user_id=query.message.chat.id)
        session.add(answered_q)
        session.commit()

        await query.message.edit_text(text=render("questions/result.html", correct=answer.correct),
                                      reply_markup=delete_markup)


@router.message(wait_answer)
async def handle_message_answer(message: types.Message, state: FSMContext):
    question_id = await state.get_value("question_id")
    msg_id = await state.get_value("msg_id")
    await state.clear()
    with conn() as session:
        lock = Pending.get_lock(session, message.chat.id)
        if not lock or lock.question_id != question_id:
            await message.answer(text=render("questions/expired.html"), reply_markup=delete_markup)
            await message.delete()
            return
        session.delete(lock)
        answer = session.query(AnswerOption).filter(
            (AnswerOption.question_id == question_id) & (AnswerOption.text == normalize_text(message.text))).first()
        question = session.get(Question, question_id)
        if answer:
            question.status = Question.QStatuses.CLOSED
        else:
            question.status = Question.QStatuses.OPEN

        answered_q = AnsweredQuestion(answer_id=answer.id, question_id=answer.question_id,
                                      user_id=message.chat.id)
        session.add(answered_q)
        session.commit()

        await message.bot.edit_message_text(text=render("questions/result.html", correct=bool(answer)),
                                            reply_markup=delete_markup, message_id=msg_id)
        await message.delete()

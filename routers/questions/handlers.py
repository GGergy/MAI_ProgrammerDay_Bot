from aiogram import types, Router
from aiogram.types import CallbackQuery

from routers.questions.callbacks import GiveAnswer
from routers.shared.handlers import terminator
from routers.shared.keyboards import delete_markup
from utils.models import conn, AnswerOption, AnsweredQuestion, Question
from utils.templateutil import render

router = Router(name=__name__)


@router.callback_query(GiveAnswer.filter())
async def handle_button_answer(query: CallbackQuery, callback_data: GiveAnswer):
    terminator.free(query.message.chat.id)
    with conn() as session:
        answer = session.get(AnswerOption, callback_data.answer_id)

        question = session.get(Question, answer.question_id)
        if answer.correct:
            question.status = Question.QStatuses.CLOSED
        else:
            question.status = Question.QStatuses.OPEN

        answered_q = AnsweredQuestion(answer_id=answer.id, question_id=answer.question_id,
                                      user_id=query.message.chat.id)
        session.add(answered_q)
        session.commit()

        await query.message.edit_text(text=render("questions/result.html", answer=answer), reply_markup=delete_markup)

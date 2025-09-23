from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from routers.questions.callbacks import ReceiveQuestion, SelectCategory, SelectDifficulty
from utils.templateutil import render

from routers.questions.keyboards import gen_cat_markup, gen_difficulty_markup
from routers.shared.keyboards import delete_markup, menu_markup
from routers.questions.states import QuestionStates

router = Router(name=__name__)


@router.callback_query(ReceiveQuestion.filter())
async def handle_receive_question(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text(
        text=render("questions/select_category.html"),
        reply_markup=gen_cat_markup(),
    )
    await query.answer()


@router.callback_query(SelectCategory.filter())
async def handle_select_category(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text(
        text=render("questions/select_difficulty.html"),
        reply_markup=gen_difficulty_markup(),
    )
    await query.answer()


@router.callback_query(SelectDifficulty.filter())
async def handle_select_difficulty(query: CallbackQuery, state: FSMContext):
    question = {"text": "чему равно 2+2", "question_type": "foo"}
    await query.message.edit_text(
        text=render("questions/question.html", question=question),
    )
    await query.answer()
    await state.set_state(QuestionStates.question)
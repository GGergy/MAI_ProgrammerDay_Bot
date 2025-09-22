from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from routers.main_menu.callbacks import ReceiveQuestion, CheckProfile

from utils.templateutil import render


router = Router(name=__name__)


@router.callback_query(ReceiveQuestion.filter())
async def handle_receive_question(query: CallbackQuery, state: FSMContext):
    #TODO Сделать вопросики
    pass
'''
@router.callback_query(CheckProfile.filter())
async def handle_check_profile(query: CallbackQuery, state: FSMContext):
    msg_id = query.message.message_id
    user = await state.get_data()
    print(user)
    await query.message.bot.edit_message_text(
        text=render("main_menu/profile.html", user=user),
        chat_id=query.message.chat.id,
        message_id=msg_id,
    )
    await state.update_data(msg_id=msg_id)
    await query.answer()
'''
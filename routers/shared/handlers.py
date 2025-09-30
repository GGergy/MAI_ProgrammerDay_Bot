import asyncio

from aiogram import types, Router
from aiogram.fsm.context import FSMContext

from routers.auth.states import RegisterStates
from routers.shared.callbacks import DeleteCallback, MenuCallback
from routers.main_menu.keyboards import main_menu_keyboard

from utils.models import conn, User, Question
from utils.templateutil import render
from utils.config import settings

router = Router(name=__name__)


class Terminator:
    def __init__(self):
        self._users = set()

    def check_lock(self, user_id: int) -> bool:
        return user_id in self._users

    def malloc(self, question_id: int, user_id: int) -> None:
        self._users.add(user_id)
        asyncio.create_task(self._terminate(question_id, user_id))

    def free(self, user_id: int) -> None:
        if user_id in self._users:
            self._users.remove(user_id)

    async def _terminate(self, question_id: int, user_id: int) -> None:
        await asyncio.sleep(settings.answer_timeout)
        with conn() as session:
            self.free(user_id)
            question = session.get(Question, question_id)
            if question.status == Question.QStatuses.PENDING:
                question.status = Question.QStatuses.OPEN
                session.commit()


terminator = Terminator()

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


@router.message()
async def deleter(message: types.Message):
    await message.delete()

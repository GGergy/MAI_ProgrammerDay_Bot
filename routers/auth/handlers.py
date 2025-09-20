from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from routers.auth.states import RegisterStates
from routers.shared.keyboards import delete_markup
from utils.models import conn, User, Faculty
from utils.templateutil import render

router = Router(name=__name__)


@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    with conn() as session:
        user = session.get(User, message.chat.id)
    msg = await message.answer(text=render("auth/hello.html", user=user))
    if not user:
        print(1)
        await state.set_state(RegisterStates.username)
        await state.update_data(msg_id=msg.message_id)
    await message.delete()


@router.message(RegisterStates.username)
async def handle_register_username(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer(text=render("shared/incorrect_message.html", exception="Сообщение пустое"),
                             reply_markup=delete_markup)
        await message.delete()
        return
    await state.update_data(username=message.text)
    msg_id = await state.get_value("msg_id")
    await message.bot.edit_message_text(text=render("auth/enter_faculty.html", username=message.text),
                                        chat_id=message.chat.id, message_id=msg_id)
    await message.delete()
    await state.set_state(RegisterStates.faculty)


@router.message(RegisterStates.faculty)
async def handle_register_faculty(message: types.Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer(text=render("shared/incorrect_message.html",
                                         exception="Сообщение пустое" if not message.text else "Факультет должен быть числом"),
                             reply_markup=delete_markup)
        await message.delete()
        return
    with conn() as session:
        faculty = session.get(Faculty, int(message.text))
    if not faculty:
        await message.answer(text=render("shared/incorrect_message.html",
                                         exception="Такого факультета не существует!"), reply_markup=delete_markup)
        await message.delete()
        return
    data = await state.get_data()
    await message.bot.edit_message_text(text=render("auth/check_data.html", username=data["username"], faculty=faculty.id),
                                        chat_id=message.chat.id, message_id=data["msg_id"])
    await state.clear()
    await message.delete()
    # дальше должна быть клавиатура с кнопками подтвердить/перезаполнить, в случае подтвердить сохраняем юзера в бд, в случае перезаполнить возвращаем state на register_username

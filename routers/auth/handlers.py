from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from routers.auth.states import RegisterStates
from routers.shared.keyboards import delete_markup
from routers.auth.keyboards import confirmation_keyboard
from utils.models import conn, User, Faculty
from utils.templateutil import render

router = Router(name=__name__)


@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    with conn() as session:
        user = session.get(User, message.chat.id)
    msg = await message.answer(text=render("assets/templates/auth/hello.html", user=user))
    if not user:
        print(1)
        await state.set_state(RegisterStates.username)
        await state.update_data(msg_id=msg.message_id)
    await message.delete()


@router.message(RegisterStates.username)
async def handle_register_username(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer(text=render("assets/templates/shared/incorrect_message.html", exception="Сообщение пустое"),
                             reply_markup=delete_markup)
        await message.delete()
        return
    await state.update_data(username=message.text)
    msg_id = await state.get_value("msg_id")
    await message.bot.edit_message_text(text=render("assets/templates/auth/enter_faculty.html", username=message.text),
                                        chat_id=message.chat.id, message_id=msg_id)
    await message.delete()
    await state.set_state(RegisterStates.faculty)


@router.message(RegisterStates.faculty)
async def handle_register_faculty(message: types.Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer(text=render("assets/templates/shared/incorrect_message.html",
                                         exception="Сообщение пустое" if not message.text else "Факультет должен быть числом"),
                             reply_markup=delete_markup)
        await message.delete()
        return
    with conn() as session:
        #заглушка для отладки кода без БД
        faculty = 2
        #faculty = session.get(Faculty, int(message.text))
    if not faculty:
        await message.answer(text=render("assets/templates/shared/incorrect_message.html",
                                         exception="Такого факультета не существует!"), reply_markup=delete_markup)
        await message.delete()
        return
    data = await state.get_data()
    
    # дальше должна быть клавиатура с кнопками подтвердить/перезаполнить, в случае подтвердить сохраняем юзера в бд, в случае перезаполнить возвращаем state на register_username
    # Вакханалия начинается здесь

    await message.bot.edit_message_text(
        text=render("assets/templates/auth/check_data.html", username=data["username"], faculty=2),
        chat_id=message.chat.id, 
        message_id=data["msg_id"], 
        reply_markup=confirmation_keyboard
    )
    await message.delete()
    
@router.callback_query(lambda callback: callback.data == "confirm")
async def handle_inline_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # Сохраняем пользователя в БД
    await state.clear()
    await callback.message.edit_text(text=render("assets/templates/auth/finish_registration.html")) # шаблоны
    await callback.answer()
    
@router.callback_query(lambda callback: callback.data == "restart")
async def handle_inline_restart(callback: CallbackQuery, state: FSMContext):
    msg_id = callback.message.message_id
    await callback.message.bot.edit_message_text(
        text=render("assets/templates/auth/restart_registration.html", username=callback.message.text),
        chat_id=callback.message.chat.id, 
        message_id=msg_id
    )
    await state.set_state(RegisterStates.username)
    await state.update_data(msg_id=msg_id)
    await callback.answer()

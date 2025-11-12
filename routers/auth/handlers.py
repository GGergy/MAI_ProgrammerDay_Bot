from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from routers.auth.states import RegisterStates
from routers.auth.keyboards import confirmation_keyboard
from routers.main_menu.keyboards import main_menu_keyboard
from routers.auth.callbacks import ConfirmProfileReg, RecreateProfileReg
from routers.shared.keyboards import delete_markup
from utils.models import conn, User, Faculty
from utils.templateutil import render

router = Router(name=__name__)


@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    with conn() as session:
        user = session.get(User, message.chat.id)
    if not user: # if not authorized
        msg = await message.answer(text=render("auth/hello.html", user=user))
        await state.set_state(RegisterStates.username) 
    else: # if authorized (already in database)
        msg = await message.answer(text=render("auth/hello.html", user=user), 
                                   reply_markup=main_menu_keyboard)
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
    await state.update_data(faculty_id=faculty.id)
    data = await state.get_data()
    await message.bot.edit_message_text(
        text=render("auth/check_data.html", username=data["username"], faculty=data["faculty_id"]),
        chat_id=message.chat.id,
        message_id=data["msg_id"],
        reply_markup=confirmation_keyboard
    )
    await message.delete()


@router.callback_query(ConfirmProfileReg.filter())
async def handle_inline_confirm(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    with conn() as session:
        user = User(telegram_id=query.message.chat.id, username=data["username"], faculty_id=data["faculty_id"])
        session.add(user)
        session.commit()
    await state.clear()
    await query.message.edit_text(text=render("auth/finish_registration.html"))
    await query.answer()


@router.callback_query(RecreateProfileReg.filter())
async def handle_inline_restart(query: CallbackQuery, state: FSMContext):
    msg_id = query.message.message_id
    await query.message.bot.edit_message_text(
        text=render("auth/restart_registration.html", username=query.message.text),
        chat_id=query.message.chat.id,
        message_id=msg_id,
        reply_markup=delete_markup,
    )
    await state.set_state(RegisterStates.username)
    await state.update_data(msg_id=msg_id)
    await query.answer()

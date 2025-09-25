from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from routers.main_menu.callbacks import CheckProfile, CheckLadder, CheckPrizes, CheckProgress
from routers.shared.keyboards import delete_markup, menu_markup

from utils.templateutil import render, horizontal_map
from utils.models import conn, User


router = Router(name=__name__)

@router.callback_query(CheckProfile.filter())
async def handle_check_profile(query: CallbackQuery, state: FSMContext):
    with conn() as session:
        user = session.get(User, query.message.chat.id)
    await query.message.edit_text(
        text=render("main_menu/profile.html", user=user),
        reply_markup=menu_markup,
    )
    await query.answer()
    

@router.callback_query(CheckProgress.filter())
async def handle_check_progress(query: CallbackQuery, state: FSMContext):
    with conn() as session:
        user = session.get(User, query.message.chat.id)
    #config TODO Переместить в конфиг
    total_number_of_questions = 12
    gifts_indexes = (11, 5)
    
    number_of_answered = 1 
    elems = [str(x) for x in range(1, total_number_of_questions+1)]
    for i in gifts_indexes:
        elems[i] = "🎁"
    elems[number_of_answered] = "🐇"
    
    await query.message.edit_text(
        text=render(
            template_name="main_menu/progress.html", 
            user=user, 
            snake_map=horizontal_map.generate_map(elems, 6),
        ),
        reply_markup=menu_markup,
    )
    await query.answer()


@router.callback_query(CheckLadder.filter())
async def handle_check_ladder(query: CallbackQuery, state: FSMContext):
    #TODO LADDER
    #with conn() as session:
    #    user = session.get(User, query.message.chat.id)
    #    ladder = ladder.get_ladder(faculty_id=user.faculty_id, page=0)
    ladder = [
        {"username": "Агния", "score": 1000},
        {"username": "Богдан", "score": 900},
        {"username": "Валерий", "score": 800},
        {"username": "Григорий", "score": 700},
        {"username": "Дмитрий", "score": 600},
        {"username": "Егор", "score": 500},
        {"username": "Женя", "score": 400},
        {"username": "Зелимхан", "score": 300},
        {"username": "Иван", "score": 200},
        {"username": "Кристина", "score": 100},
             
    ] 
    await query.message.edit_text(
        text=render("main_menu/ladder.html", ladder=ladder, page=0),
        reply_markup=menu_markup,
    )
    await query.answer()


@router.callback_query(CheckPrizes.filter())
async def handle_check_ladder(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text(
        text=render("main_menu/prizes.html"),
        reply_markup=menu_markup,
    )
    await query.answer()
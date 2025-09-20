import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен бота
API_TOKEN = '8292941228:AAGdBOz2G960O1dPiWJfqmbEpfIdDS7y3hY'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Хранилище данных пользователей
users_data = {}


# Состояния для FSM
class ProfileStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_faculty = State()


# Добавляем банк вопросов (в начало файла, после импортов)
questions_bank = [
    {
        "question": "Столица России?",
        "options": ["Москва", "Санкт-Петербург", "Казань", "Новосибирск"],
        "correct_answer": 0
    },
    {
        "question": "2 + 2 = ?",
        "options": ["3", "4", "5", "6"],
        "correct_answer": 1
    },
    {
        "question": "Самая большая планета Солнечной системы?",
        "options": ["Земля", "Марс", "Юпитер", "Сатурн"],
        "correct_answer": 2
    }
]


# Добавляем состояние для ожидания ответа на вопрос
class QuizStates(StatesGroup):
    waiting_for_answer = State()


# Клавиатуры
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Профиль")],
            [KeyboardButton(text="Решить вопрос")]  # Добавляем кнопку
        ],
        resize_keyboard=True
    )


def get_auth_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Авторизоваться")]],
        resize_keyboard=True
    )


def get_edit_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Имя"), KeyboardButton(text="Факультет")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )


# Команда старт
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if user_id not in users_data:
        users_data[user_id] = {
            "name": "Не указано",
            "faculty": "Не указано",
            "points": 0,
            "energy": 100,
            "solved_questions": 0,  # Добавляем количество решенных вопросов
            "profile_completed": False
        }

        await message.answer(
            "👋 Добро пожаловать! Заполните ваш профиль.\n\n"
            "Нажмите кнопку ниже чтобы начать:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Заполнить профиль")]],
                resize_keyboard=True
            )
        )
    else:
        await message.answer(
            "С возвращением! Вот ваше меню:",
            reply_markup=get_main_keyboard()
        )


# Кнопка заполнения профиля
@dp.message(lambda message: message.text == "Заполнить профиль")
async def start_profile_fill(message: types.Message):
    user_id = message.from_user.id

    if user_id not in users_data:
        users_data[user_id] = {
            "name": "Не указано",
            "faculty": "Не указано",
            "points": 0,
            "profile_completed": False
        }

    user_data = users_data[user_id]

    if user_data["profile_completed"]:
        await message.answer("❌ Профиль уже заполнен и не может быть изменен.")
        return

    await message.answer(
        "📝 Заполните ваш профиль. Что вы хотите изменить?",
        reply_markup=get_edit_keyboard()
    )


# Кнопка профиля
@dp.message(lambda message: message.text == "Профиль")
async def show_profile(message: types.Message):
    user_id = message.from_user.id

    if user_id not in users_data:
        await message.answer("Сначала необходимо заполнить профиль!", reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Заполнить профиль")]],
            resize_keyboard=True
        ))
        return

    user_data = users_data[user_id]

    profile_text = (
        f"👤 <b>Профиль</b>\n\n"
        f"🏷️ <b>Имя:</b> {user_data['name']}\n"
        f"🎓 <b>Факультет:</b> {user_data['faculty']}\n"
        f"⭐ <b>Очки:</b> {user_data['points']}\n"
        f"⚡ <b>Энергия:</b> {user_data.get('energy', 100)}/100\n"
        f"✅ <b>Решено вопросов:</b> {user_data.get('solved_questions', 0)}\n"  # Добавляем решенные вопросы
        f"📊 <b>Статус:</b> {'✅ Заполнен' if user_data['profile_completed'] else '⚠️ Требует заполнения'}"
    )

    await message.answer(profile_text, parse_mode='HTML')


# Обработка выбора поля для редактирования
@dp.message(lambda message: message.text in ["Имя", "Факультет"])
async def choose_field_to_edit(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if user_id not in users_data:
        await message.answer("Сначала необходимо заполнить профиль!", reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Заполнить профиль")]],
            resize_keyboard=True
        ))
        return

    if users_data[user_id]["profile_completed"]:
        await message.answer("❌ Профиль уже заполнен и не может быть изменен.")
        return

    field = message.text.lower()

    if field == "имя":
        await state.set_state(ProfileStates.waiting_for_name)
        await message.answer("Введите ваше имя:", reply_markup=types.ReplyKeyboardRemove())
    elif field == "факультет":
        await state.set_state(ProfileStates.waiting_for_faculty)
        await message.answer("Введите ваш факультет:", reply_markup=types.ReplyKeyboardRemove())


# Кнопка назад
@dp.message(lambda message: message.text == "Назад")
async def back_to_main(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == QuizStates.waiting_for_answer:
        await state.clear()
        await message.answer("Выход из режима вопросов.", reply_markup=get_main_keyboard())
    else:
        await state.clear()
        user_id = message.from_user.id

        if user_id in users_data and users_data[user_id]["profile_completed"]:
            await message.answer("Главное меню:", reply_markup=get_main_keyboard())
        else:
            await message.answer(
                "Заполните профиль чтобы продолжить:",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text="Заполнить профиль")]],
                    resize_keyboard=True
                )
            )


# Обработка ввода имени
@dp.message(ProfileStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if message.text.strip() == "":
        await message.answer("Имя не может быть пустым. Попробуйте еще раз:")
        return

    users_data[user_id]["name"] = message.text
    await check_profile_completion(user_id)
    await state.clear()

    if users_data[user_id]["profile_completed"]:
        await message.answer("✅ Имя успешно обновлено! Профиль завершен!", reply_markup=get_main_keyboard())
    else:
        await message.answer("✅ Имя успешно обновлено! Что дальше?", reply_markup=get_edit_keyboard())


# Обработка ввода факультета
@dp.message(ProfileStates.waiting_for_faculty)
async def process_faculty(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if message.text.strip() == "":
        await message.answer("Факультет не может быть пустым. Попробуйте еще раз:")
        return

    users_data[user_id]["faculty"] = message.text
    await check_profile_completion(user_id)
    await state.clear()

    if users_data[user_id]["profile_completed"]:
        await message.answer("✅ Факультет успешно обновлен! Профиль завершен!", reply_markup=get_main_keyboard())
    else:
        await message.answer("✅ Факультет успешно обновлен! Что дальше?", reply_markup=get_edit_keyboard())


# Проверка завершения профиля
async def check_profile_completion(user_id):
    user_data = users_data[user_id]

    # Проверяем, что все поля заполнены и не равны значениям по умолчанию
    if (user_data["name"] != "Не указано" and
            user_data["faculty"] != "Не указано" and
            user_data["name"].strip() != "" and
            user_data["faculty"].strip() != ""):
        users_data[user_id]["profile_completed"] = True


# Обработчик кнопки "Решить вопрос"
# Обновляем обработчик кнопки "Решить вопрос"
@dp.message(lambda message: message.text == "Решить вопрос")
async def solve_question(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if user_id not in users_data:
        await message.answer("Сначала необходимо заполнить профиль!", reply_markup=get_auth_keyboard())
        return

    # Проверяем достаточно ли энергии
    if users_data[user_id].get("energy", 100) < 20:
        await message.answer("❌ Недостаточно энергии! Нужно 20 единиц.", reply_markup=get_main_keyboard())
        return

    # Выбираем случайный вопрос
    import random
    question_data = random.choice(questions_bank)

    # Создаем клавиатуру с вариантами ответов
    options_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=option)] for option in question_data["options"]],
        resize_keyboard=True
    )

    # Списываем энергию
    users_data[user_id]["energy"] -= 20

    # Сохраняем данные вопроса в состоянии
    await state.set_state(QuizStates.waiting_for_answer)
    await state.update_data(
        correct_index=question_data["correct_answer"],
        correct_answer=question_data["options"][question_data["correct_answer"]]
    )

    await message.answer(
        f"❓ <b>Вопрос:</b> {question_data['question']}\n\n"
        f"⚡ <b>Потрачено энергии:</b> 20\n"
        f"🔋 <b>Осталось энергии:</b> {users_data[user_id]['energy']}\n\n"
        "Выберите правильный ответ:",
        reply_markup=options_keyboard,
        parse_mode='HTML'
    )


# Обновляем обработчик ответов на вопросы (добавляем информацию об энергии)
@dp.message(QuizStates.waiting_for_answer)
async def process_answer(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_answer = message.text

    # Получаем данные из состояния
    data = await state.get_data()
    correct_answer = data["correct_answer"]
    correct_index = data["correct_index"]

    # Проверяем ответ
    if user_answer == correct_answer:
        # Правильный ответ
        users_data[user_id]["points"] += 1
        users_data[user_id]["solved_questions"] += 1
        response_text = (
            "✅ <b>Правильно!</b>\n"
            "+1 очко\n"
            "+1 к решенным вопросам\n"
            f"⚡ <b>Энергия:</b> {users_data[user_id]['energy']}/100"
        )
    else:
        # Неправильный ответ
        response_text = (
            f"❌ <b>Неправильно!</b>\n"
            f"Правильный ответ: {correct_answer}\n"
            f"⚡ <b>Энергия:</b> {users_data[user_id]['energy']}/100"
        )

    await state.clear()
    await message.answer(response_text, parse_mode='HTML', reply_markup=get_main_keyboard())


# Команда для просмотра всех пользователей (для отладки)
@dp.message(Command("users"))
async def show_users(message: types.Message):
    user_id = message.from_user.id

    if len(users_data) == 0:
        await message.answer("Пользователей пока нет.")
        return

    users_list = "📊 Список пользователей:\n\n"
    for uid, data in users_data.items():
        users_list += f"ID: {uid}\nИмя: {data['name']}\nФакультет: {data['faculty']}\nОчки: {data['points']}\nЭнергия: {data.get('energy', 100)}\nРешено вопросов: {data.get('solved_questions', 0)}\nСтатус: {'✅' if data['profile_completed'] else '⚠️'}\n\n"
    await message.answer(users_list)


# Добавляем команду для проверки энергии
@dp.message(Command("energy"))
async def check_energy(message: types.Message):
    user_id = message.from_user.id

    if user_id not in users_data:
        await message.answer("Сначала необходимо заполнить профиль!")
        return

    await message.answer(
        f"⚡ <b>Ваша энергия:</b> {users_data[user_id].get('energy', 100)}/100\n"
        "Каждый вопрос тратит 20 энергии",
        parse_mode='HTML'
    )


# Команда для сброса своего профиля
@dp.message(Command("reset_me"))
async def reset_my_profile(message: types.Message):
    user_id = message.from_user.id

    if user_id in users_data:
        users_data[user_id] = {
            "name": "Не указано",
            "faculty": "Не указано",
            "points": 0,
            "energy": 100,
            "solved_questions": 0,  # Добавляем сброс решенных вопросов
            "profile_completed": False
        }

        await message.answer(
            "✅ Ваш профиль сброшен. Вы можете заполнить его заново.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Заполнить профиль")]],
                resize_keyboard=True
            )
        )
    else:
        await message.answer("У вас еще нет профиля для сброса.")


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
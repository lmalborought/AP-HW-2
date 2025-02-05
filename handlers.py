from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram import Router, F
from googletrans import Translator
from functions import *
from states import *
from config import API_KEY_wether, API_KEY_sport, API_KEY_food
from datetime import datetime
from keyboards import settings
import matplotlib.pyplot as plt

router = Router()

translator = Translator()

users = {}


@router.message(Command('start'))
async def start(message: Message):
    await message.reply('Для начала работы, необходимо заполнить профиль /set_profile')


@router.message(Command('set_profile'))
async def set_profile(message: Message, state: FSMContext):
    await message.reply('Введите ваше имя.')
    await state.set_state(User.name)


@router.message(User.name)
async def set_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply('Введите ваш возраст.')
    await state.set_state(User.age)


@router.message(User.age)
async def set_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        await state.update_data(age=age)
        await message.reply('Введите ваш рост (см).')
        await state.set_state(User.height)
    except ValueError:
        await message.reply("Некоректно введен возраст.")


@router.message(User.height)
async def set_height(message: Message, state: FSMContext):
    try:
        height = int(message.text)
        await state.update_data(height=height)
        await message.reply('Введите ваш вес(кг).')
        await state.set_state(User.weight)
    except ValueError:
        await message.reply("Некоректно введен вес.")


@router.message(User.weight)
async def set_weight(message: Message, state: FSMContext):
    try:
        weight = int(message.text)
        await state.update_data(weight=weight)
        await message.reply('Введите город в котором вы находитесь.')
        await state.set_state(User.city)
    except ValueError:
        await message.reply("Некоректно введен рост")


@router.message(User.city)
async def set_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.reply('''Вы можете ввести желаемую норму колорий, или введите '0' и норма будет расчитана нами.''')
    await state.set_state(User.calorie_goal)


@router.message(User.calorie_goal)
async def set_calorie_goal(message: Message, state: FSMContext):
    calorie_goal = int(message.text)
    data = await state.get_data()
    name, age, height, weight, city = data['name'], data['age'], data['height'], data['weight'], data['city']
    if calorie_goal == 0:
        calorie_goal = calorie_count(weight, height, age)
    users[message.from_user.id] = {
        'name': name.title(),
        'age': age,
        'height': height,
        'weight': weight,
        'city': city.title(),
        'water_goal': water_count(weight),
        'calorie_goal': calorie_goal,
        "logged_water": 0,
        "logged_calories": 0,
        "burned_calories": 0,
        'last_update': datetime.now().date()
    }
    await message.reply(f'✔️ {name}, ваш профиль готов! Для просмотра комманд нажмите /help')
    await state.clear()


@router.message(Command('help'))
async def get_help(message: Message):
    await message.reply(f'Вот список всех команд:\n'
                        f'/help - Список всех команд\n'
                        f'/log_water - Записать количество выпитой воды\n'
                        f'/log_food - Записать количество потребленной пищи\n'
                        f'/log_workout - Записать тренировки\n'
                        f'/check_progress - Просмотр прогресса за день\n'
                        f'/check_progress_graph - Просмотр график прогресса\n'
                        f'/see_profile - Просмотр профиля\n'
                        f'/change_profile - зменение профиля\n'
                        f'/get_advice - Полезные рекомендации'
                        )


@router.message(Command('log_water'))
async def logging_water(message: Message):
    try:
        user = users.get(message.from_user.id)
        await day(user)
        log_water = message.text.split()
        if len(log_water) < 2:
            await message.reply('Пожалуйста введите количество воды через пробел')
        else:
            user['logged_water'] += int(log_water[1])
            await message.reply(f"{user['name']}, вы выпили {log_water[1]} мл воды, осталось выпить"
                                f" {user['water_goal'] - user['logged_water']} мл")
    except ValueError:
        await message.reply("Попробуйте ввести в формате /log_water <количество>")


@router.message(Command('log_food'))
async def log_food(message: Message, state: FSMContext):
    await message.reply('Напишите что вы съели.')
    await state.set_state(Food.name)


@router.message(Food.name)
async def food_name(message: Message, state: FSMContext):
    try:
        name = message.text
        await state.update_data(name=name)
        await message.reply('Введите количество в граммах.')
        await state.set_state(Food.amount)
    except ValueError:
        await message.reply("Некоректно введен продукт")


@router.message(Food.amount)
async def food_amount(message: Message, state: FSMContext):
    user = users.get(message.from_user.id)
    await day(user)
    amount = message.text
    data = await state.get_data()
    name = data['name']
    total_calories = get_calorie(f'{amount}g {await translate(name)}', API_KEY_food)
    user['logged_calories'] += total_calories
    await message.reply(f'{user["name"]}, вы съели {amount}г {name}. Записано: {total_calories} ккал.')
    await state.clear()


@router.message(Command('change_profile'))
async def change_profile(message: Message, state: FSMContext):
    await message.reply('Введите ваш возраст.')
    await state.set_state(UserChange.age)


@router.message(UserChange.age)
async def change_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        await state.update_data(age=age)
        await message.reply('Введите ваш вес(кг).')
        await state.set_state(UserChange.weight)
    except ValueError:
        await message.reply("Некоректно введен возраст.")


@router.message(UserChange.weight)
async def change_weight(message: Message, state: FSMContext):
    try:
        weight = int(message.text)
        await state.update_data(weight=weight)
        await message.reply('Введите город в котором вы находитесь.')
        await state.set_state(UserChange.city)
    except ValueError:
        await message.reply("Некоректно введен вес")


@router.message(UserChange.city)
async def set_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.reply('''Вы можете ввести желаемую норму колорий, или введите '0' и норма будет расчитана нами.''')
    await state.set_state(UserChange.calorie_goal)


@router.message(UserChange.calorie_goal)
async def change_city(message: Message, state: FSMContext):
    user = users.get(message.from_user.id)
    calorie_goal = int(message.text)
    data = await state.get_data()
    age, weight, city = data['age'], data['weight'], data['city']
    if calorie_goal == 0:
        calorie_goal = calorie_count(weight, user['height'], age)
    user['age'] = age
    user['weight'] = weight
    user['city'] = city.title()
    user['water_goal'] = water_count(weight)
    user['calorie_goal'] = calorie_goal
    await message.reply(f'✔️ {user["name"]}, ваш профиль изменен!')
    await state.clear()


@router.message(Command('get_advice'))
async def get_advice(message: Message):
    await message.answer(f'Выберете:', reply_markup=settings)


@router.callback_query(F.data == 'low_calory')
async def get_advice(callback: CallbackQuery):
    await callback.answer('Вы выбрали Список низкокалорийных продуктов')
    await callback.message.answer(f'🔸 Натуральный йогурт без добавок и наполнителей - 55 кКал 100г.\n'
                                  f'🔸 Куриная или индюшачья грудка - 239-189 кКал 100г.\n'
                                  f'🔸 Морепродукты - 90-100 кКал 100г.\n'
                                  f'🔸 Белая нежирная рыба - 70–100 кКал 100г.\n'
                                  f'🔸 Творог 0-2% жирности - 74,4 кКал 100г.\n'
                                  f'🔸 Тофу - 83 кКал 100г.\n'
                                  f'🔸 Кефир 0-1% жирности - 40 кКал 100г.\n')


@router.callback_query(F.data == 'sport_ideas')
async def get_advice(callback: CallbackQuery):
    await callback.answer('Вы выбрали Идеи упражнений')
    await callback.message.answer(f'🔹 Скакалка - за минуту можно сжечь 14-15 ккал.\n'
                                  f'🔹  Приседания - можно потратить 53,6 ккал за 4 минуты.\n'
                                  f'🔹 Бёрпи - на одно бёрпи (отжимание с подпрыгванием) затрачивается 1,40 ккал\n'
                                  f'🔹 Плавание - плавание брассом сжигает порядка 750 килокалорий, а на спине — 600.\n'
                                  f'🔹 Велоспорт - можно сжечь ~600 килокалорий за часовую велосипедную поездку.\n'
                                  f'🔹 Бег - час бега с темпом 7 мин. за км сжигает порядка 600 килокалорий.\n')


@router.message(Command('check_progress_graph'))
async def check_progress_graph(message: Message):
    user = users.get(message.from_user.id)
    await day(user)

    labels = ['Выпито воды', 'Осталось']
    calorie_labels = ['Потреблено ккал', 'Осталось']

    water_values = [user['logged_water'], max(0, user['water_goal'] - user['logged_water'])]
    calorie_values = [user['logged_calories'], max(0, user['calorie_goal'] - user['logged_calories'])]

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    axes[0].pie(water_values, labels=labels, colors=['#3674B5', '#A1E3F9'], autopct='%1.1f%%')
    axes[0].set_title('Прогресс по воде')
    axes[1].pie(calorie_values, labels=calorie_labels, colors=['#F72C5B', '#FF748B'], autopct='%1.1f%%')
    axes[1].set_title('Прогресс по калориям')

    plt.savefig("progress.png", format='png')
    image = FSInputFile("progress.png")
    await message.answer_photo(image)


@router.message(Command('see_profile'))
async def see_profile(message: Message):
    user = users.get(message.from_user.id)
    await day(user)
    await message.reply(f"Ваши настройки:\n"
                        f"Имя: {user['name']}\n"
                        f"Возраст: {user['age']}\n"
                        f"Вес: {user['weight']}\n"
                        f"Рост: {user['height']}\n"
                        )


@router.message(Command('log_workout'))
async def log_workout(message: Message):
    user = users.get(message.from_user.id)
    await day(user)
    try:
        activity, duration = message.text.split()[1:]
        count_calories = calorie_burned(await translate(activity), int(duration), API_KEY_sport)
        user['burned_calories'] += count_calories
        water = (int(duration) // 30) * 200
        user['water_goal'] += water
        await message.reply(f"💪 {user['name']}, вы выполнили тренировку {activity} {duration} минут - {count_calories} ккал.\n"
                            f"Дополнительно: выпейте {water} мл воды.")
    except ValueError:
        await message.reply('Попробуйте ввести еще раз а таком формате /log_workout <типтренировки> <время(мин)>')


@router.message(Command('check_progress'))
async def check_progress(message: Message):
    user = users.get(message.from_user.id)
    await day(user)
    await message.reply(f"📊 Прогресс:\n"
                        f"Вода:\n"
                        f"- Выпито: {user['logged_water']} мл из {user['water_goal']}\n"
                        f"- Осталось: {user['water_goal'] - user['logged_water']} мл.\n"
                        f"Калории:\n"
                        f"- Потреблено: {user['logged_calories']} ккал из {user['calorie_goal']} ккал.\n"
                        f"- Сожжено: {user['burned_calories']} ккал.\n"
                        f"- Баланс: {user['calorie_goal'] - user['logged_calories']} ккал.")


async def translate(text):
    translated = await translator.translate(text, src='ru', dest='en')
    return translated.text


async def day(user):
    if user['last_update'] < datetime.now().date():
        user['logged_water'] = 0
        user['logged_calories'] = 0
        user['burned_calories'] = 0
        weather = get_temp(await translate(user['city']), API_KEY_wether)
        if weather < 25:
            user['water_goal'] = water_count(user['weight'])
        else:
            user['water_goal'] = water_count(user['weight']) + 600

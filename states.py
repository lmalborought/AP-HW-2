from aiogram.fsm.state import StatesGroup, State


class User(StatesGroup):
    name = State()
    age = State()
    height = State()
    weight = State()
    city = State()
    calorie_goal = State()


class UserChange(StatesGroup):
    age = State()
    weight = State()
    city = State()
    calorie_goal = State()


class Food(StatesGroup):
    name = State()
    amount = State()

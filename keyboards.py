from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup

settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Полезные рецепты', url='https://av.ru/ideas/recipe_list/themes/poleznye-blyuda/')],
    [InlineKeyboardButton(text='Список низкокалорийных продуктов', callback_data='low_calory')],
    [InlineKeyboardButton(text='Идеи упражнений', callback_data='sport_ideas')]
    ])

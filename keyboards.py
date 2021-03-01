from telebot import types

YesNoMenu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
item1 = types.KeyboardButton("Да")
item2 = types.KeyboardButton("Нет")
YesNoMenu.add(item1, item2)

StartQuestions = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
item1 = types.KeyboardButton("История компании")
item2 = types.KeyboardButton("Корпаративная культура")
item3 = types.KeyboardButton("Нормативные документы")
StartQuestions.add(item1, item2, item3)


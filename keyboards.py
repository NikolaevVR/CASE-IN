from telebot import types
YesNoMenu = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1 = types.KeyboardButton("Да")
item2 = types.KeyboardButton("Нет")
YesNoMenu.add(item1, item2)
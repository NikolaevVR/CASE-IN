from telebot import types

YesNoMenu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
item1 = types.KeyboardButton("Да")
item2 = types.KeyboardButton("Нет")
YesNoMenu.add(item1, item2)

# StartQuestions = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
# item1 = types.KeyboardButton("История компании")
# item2 = types.KeyboardButton("Корпаративная культура")
# item3 = types.KeyboardButton("Нормативные документы")
# StartQuestions.add(item1, item2, item3)

StartQuestions = types.InlineKeyboardMarkup()
item1 = types.InlineKeyboardButton(text='История компании', url='http://www.biblioatom.ru/')
item2 = types.InlineKeyboardButton(text='Корпаративная культура', url='https://www.rosatom.ru/upload/iblock/156/156e47f4a1691c442d4a5d64fb456cee.pdf')
item3 = types.InlineKeyboardButton(text='Нормативные документы', url='https://www.rosatom.ru/upload/iblock/a42/a42fc60d74177edf55f9e4ec64618da3.pdf')
StartQuestions.add(item1)
StartQuestions.add(item2)
StartQuestions.add(item3)

Menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
item1 = types.KeyboardButton("Узнать Расписание")
item2 = types.KeyboardButton("Мои задания")
item3 = types.KeyboardButton("Найти нужный отдел")
item4 = types.KeyboardButton("Нажми если дебил")
Menu.add(item1, item2)
Menu.add(item3, item4)

Timetable1 = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
item1 = types.KeyboardButton("Своё")
item2 = types.KeyboardButton("Расписание одного из сотрудников")
Timetable1.add(item1)
Timetable1.add(item2)
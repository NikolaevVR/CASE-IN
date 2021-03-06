from telebot import types

YesNoMenu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
item1 = types.KeyboardButton("Да")
item2 = types.KeyboardButton("Нет")
YesNoMenu.add(item1, item2)


StartQuestions = types.InlineKeyboardMarkup()
item1 = types.InlineKeyboardButton(text='История компании', url='http://www.biblioatom.ru/')
item2 = types.InlineKeyboardButton(text='Корпаративная культура', url='https://www.rosatom.ru/upload/iblock/156/156e47f4a1691c442d4a5d64fb456cee.pdf')
item3 = types.InlineKeyboardButton(text='Нормативные документы', url='https://rosatom.ru/about/protivodeystvie-korruptsii/normativnye-akty-goskorporatsii-rosatom/')
StartQuestions.add(item1)
StartQuestions.add(item2)
StartQuestions.add(item3)


Menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
item1 = types.KeyboardButton("Узнать Расписание")
item2 = types.KeyboardButton("Мои задания")
item3 = types.KeyboardButton("Найти нужный отдел")
item4 = types.KeyboardButton("Отметить задание как выполненное")
Menu.add(item1, item2)
Menu.add(item3, item4)


Timetable1 = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
item1 = types.KeyboardButton("Своё")
item2 = types.KeyboardButton("Расписание одного из сотрудников")
item3 = types.KeyboardButton("Вернуться")
Timetable1.add(item2)
Timetable1.add(item1, item3)


department_choice = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
item1 = types.KeyboardButton("IT")
item2 = types.KeyboardButton("БУХГАЛТЕРСКИЙ")
item3 = types.KeyboardButton("ЗАКУПОК")
item4 = types.KeyboardButton("КАДРОВ")
item5 = types.KeyboardButton("КАЧЕСТВА")
item6 = types.KeyboardButton("ЛОГИСТИКИ")
item7 = types.KeyboardButton("РАЗВИТИЯ")
item8 = types.KeyboardButton("ТОРГОВЫЙ")
item9 = types.KeyboardButton("ФИНАНСОВ")
item10 = types.KeyboardButton("ЮРИДИЧЕСКИЙ")
department_choice.add(item1, item2)
department_choice.add(item3, item5)
department_choice.add(item4, item6)
department_choice.add(item7, item8)
department_choice.add(item9, item10)


Quests = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
item1 = types.KeyboardButton("Отметить задание как выполненное")
item2 = types.KeyboardButton("Вернуться")
Quests.add(item1, item2)




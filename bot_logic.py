import telebot
import psycopg2
import keyboards as kb
from config import bot_api, database_connect
from datetime import datetime as dt
import time
from datetime import time as t
from telebot import types
from TelegramBot import *


bot = telebot.TeleBot(bot_api)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    con = psycopg2.connect(**database_connect)
    user_id = message.from_user.id
    cursor = con.cursor()
    cursor.execute("SELECT * FROM employee WHERE telegram=%s",[user_id])
    record = cursor.fetchall()
    cursor.close()
    con.close()
    if record==[]:
        register(message)
    else:
        bot.send_message(message.from_user.id, "Приветствую", reply_markup=kb.Menu)
        Dialog(message)


def register(message):
    bot.send_message(message.from_user.id, "Здравствуйте! Мы не знакомы, давайте познакомимся."
                                           " Введите свою рабочую почту, которую Вам выдали в отделе кадров.")
    bot.register_next_step_handler(message, ask_teleID)


def ask_teleID(message):
    con = psycopg2.connect(**database_connect)
    cursor = con.cursor()
    email=str(message.text).lower()
    cursor.execute("SELECT last_name, first_name FROM employee WHERE email=%s", [email])
    record=cursor.fetchall()
    cursor.close()
    con.close()
    if record==[]:
        bot.send_message(message.from_user.id, "Кажется, Вы ввели неправильную почту."
                                               " Введите свою рабочую почту, которую Вам выдали в отделе кадров.")
        bot.register_next_step_handler(message, ask_teleID)
    else:
        rec = ''
        for a in record:
            for b in range(len(a)):
                rec = rec + a[b] + ' '
        bot.send_message(message.from_user.id, f'{rec} - это Вы?', reply_markup=kb.YesNoMenu)
        bot.register_next_step_handler(message, write_teleID, email)


def write_teleID(message,email):
    if message.text=='Да':
        con = psycopg2.connect(**database_connect)
        cursor = con.cursor()
        cursor.execute("UPDATE employee SET telegram=%s WHERE email=%s", [int(message.from_user.id), email])
        con.commit()
        cursor.close()
        con.close()
        bot.send_message(message.from_user.id, "Рад приветствовать Вас в нашей компании! \n"
                                            "Я помогу Вам освоиться и узнать как всё устроено.", reply_markup=kb.Menu)
        Dialog(message)
    else:
        bot.send_message(message.from_user.id, "Кажется, Вы ввели неправильную почту.\n"
                                               "Введите свою рабочую почту, которую Вам выдали в отделе кадров.")
        bot.register_next_step_handler(message, ask_teleID)


def get_my_id(user_id):
    con = psycopg2.connect(**database_connect)
    cursor = con.cursor()
    cursor.execute("SELECT id FROM employee WHERE telegram=%s",
                   [int(user_id)])
    id = str(cursor.fetchall()[0][0])
    cursor.close()
    con.close()
    return id


def Dialog (message):
    bot.send_message(message.from_user.id, "Можете задать мне вопрос или выбрать интересующий из списка:",
                     reply_markup=kb.StartQuestions)
    bot.register_next_step_handler(message, Menu)


def Menu(message):
    if message.text == 'Узнать Расписание':
        bot.send_message(message.from_user.id, "Чьё расписание Вы хотите узнать?", reply_markup=kb.Timetable1)
        bot.register_next_step_handler(message, timetable)
    elif message.text == 'Мои задания':
        quests(message)
    elif message.text == 'Найти нужный отдел':
        bot.send_message(message.from_user.id, "Какой отдел Вас интересует?", reply_markup=kb.department_choice)
        bot.register_next_step_handler(message, location_of_department)
    elif message.text == 'Отметить задание как выполненное':
        quest_choice(message)
    else:
        bot.send_message(message.from_user.id, bright(str(message.text)), reply_markup=kb.Menu)
        Dialog(message)


def timetable(message):
    if message.text == 'Своё':
        id = get_my_id(message.from_user.id)
        timetable_check(id, message)
    elif message.text == 'Вернуться':
        bot.send_message(message.from_user.id, "Выход в главное меню", reply_markup=kb.Menu)
        Dialog(message)
    else:
        bot.send_message(message.from_user.id, "Укажите ФИО интересующего Вас работника")
        bot.register_next_step_handler(message, FIO_check)


def FIO_check(message):
    record = []
    persons=''
    buf=message
    listFIO = message.text.split()
    con = psycopg2.connect(**database_connect)
    cursor = con.cursor()
    if len(listFIO) > 2:
        first_word = str(listFIO[0]).lower()
        first_word = first_word.title()
        second_word = str(listFIO[1]).lower()
        second_word = second_word.title()
        third_word = str(listFIO[2]).lower()
        third_word = third_word.title()
        cursor.execute("SELECT id, first_name, last_name, patronymic FROM employee "
                       "WHERE last_name=%s AND first_name=%s AND patronymic=%s",
                           [first_word, second_word, third_word])
        record=cursor.fetchall()
        if record == []:
            cursor.execute("SELECT id, first_name, last_name, patronymic FROM employee "
                           "WHERE first_name=%s AND patronymic=%s AND last_name=%s",
                           [first_word, second_word, third_word])
            record = cursor.fetchall()
    elif len(listFIO) == 2:
        first_word = str(listFIO[0]).lower()
        first_word = first_word.title()
        second_word = str(listFIO[1]).lower()
        second_word = second_word.title()
        cursor.execute("SELECT id, first_name, last_name, patronymic FROM employee WHERE "
                       "first_name=%s AND last_name=%s", [first_word, second_word])
        record=cursor.fetchall()
        if record == []:
            cursor.execute("SELECT id, first_name, last_name, patronymic FROM employee "
                           "WHERE last_name=%s AND first_name=%s",[first_word, second_word])
            record = cursor.fetchall()
            if record == []:
                cursor.execute("SELECT id, first_name, last_name, patronymic FROM employee "
                               "WHERE first_name=%s AND patronymic=%s",
                               [first_word, second_word])
                record = cursor.fetchall()
    cursor.close()
    con.close()
    if record==[] or len(listFIO) < 2:
        bot.send_message(message.from_user.id, f'Работника с именем {message.text.title()} не найдено!')
        bot.send_message(message.from_user.id, "Чьё расписание Вы хотите узнать?", reply_markup=kb.Timetable1)
        bot.register_next_step_handler(message, timetable)
    elif len(record)> 1 and len(listFIO) == 2:
        for a in range(len(record)):
            persons = persons + f'{record [a][2]}  {record [a][1]}  {record [a][3]}\n'
        bot.send_message(message.from_user.id, f'По Вашему запросу найдено несколько работников: \n{persons}\n'
                                               f'Уточникте пожалуйста чьё расписание Вы хотите узнать?\n')
        timetable(message)
    else:
        id = str(record[0][0])
        timetable_check(id, buf)


def timetable_check(id, message):
    user_id = message.from_user.id
    now_date = str(dt.fromtimestamp(int(time.time()))).split()[0]
    now_time = t.fromisoformat(str(dt.fromtimestamp(int(time.time()))).split()[1])
    con = psycopg2.connect(**database_connect)
    cursor = con.cursor()
    cursor.execute("SELECT last_name, first_name, patronymic, department, workplace, email, position "
                   "FROM employee WHERE id=%s ",
                   [int(id)])
    place=cursor.fetchall()
    cursor.execute("SELECT location FROM location_of_departments WHERE department=%s", [place[0][3]])
    location=cursor.fetchall()
    cursor.execute("SELECT time_start, time_end, appointments FROM timetable WHERE id=%s AND dat=%s AND time_end>%s",
                    [id, now_date, now_time])
    record = cursor.fetchall()
    other_days = ''
    cursor.execute("SELECT dat, time_start, time_end FROM timetable WHERE id=%s AND dat>%s ORDER BY dat",
                    [id, now_date])
    record1 = cursor.fetchall()[:3]
    cursor.close()
    con.close()
    if record1 != []:
        first_day = record1[0][0]
        first_day = first_day.strftime('%d.%m.%Y %H:%M:%S').split()[0]
        other_days = other_days + f'{first_day}:    {str(record1[0][1])[:-3]}-{str(record1[0][2])[:-3]}\n'
        second_day = record1[1][0]
        second_day = second_day.strftime('%d.%m.%Y %H:%M:%S').split()[0]
        other_days = other_days + f'{second_day}:    {str(record1[1][1])[:-3]}-{str(record1[1][2])[:-3]}\n'
        third_day = record1[2][0]
        third_day = third_day.strftime('%d.%m.%Y %H:%M:%S').split()[0]
        other_days = other_days + f'{third_day}:    {str(record1[2][1])[:-3]}-{str(record1[2][2])[:-3]}\n'
    if other_days == '':
        other_days = 'Нет данных о расписании на ближайшие дни'
    if record==[]:
        if id==get_my_id(user_id):
            bot.send_message(user_id, f'Вы сегодня не работаете)\n\n'
                                      f'Расписание на пару дней вперёд:\n'
                                      f'{other_days}',
                             reply_markup=kb.Menu)
        else:
            bot.send_message(user_id, f'Сотрудник: {place[0][0]} {place[0][1]} {place[0][2]}\n'
                                      f'Должность: {place[0][6]}\n'
                                      f'Отдел: {place[0][3]} (Рабочее место №{place[0][4]})\n\n'
                                      f'Находится по адресу: {location[0][0]}\n'
                                      f'Вы можете связаться с работником по корпоративной почте:\n{place[0][5]}\n'
                                      f'Данного работника нет на месте\n\n'
                                      f'Расписание на пару дней вперёд:\n'
                                      f'{other_days}',
                             reply_markup=kb.Menu)
        Dialog(message)
    else:
        if id==get_my_id(user_id):
            bot.send_message(user_id, f'Время работы сегодня: {str(record[0][0])[:-3]}-{str(record[0][1])[:-3]}\n'
                                      f'Сегодняшние мероприятия: {str(record[0][2])} \n\n'
                                      f'Расписание на пару дней вперёд:\n'
                                      f'{other_days}',
                             reply_markup=kb.Menu)
        else:
            bot.send_message(user_id, f'Сотрудник: {place[0][0]} {place[0][1]} {place[0][2]}\n'
                                      f'Должность: {place[0][6]}\n'
                                      f'Отдел: {place[0][3]} (Рабочее место №{place[0][4]})\n\n'
                                      f'Находится по адресу: {location[0][0]}\n'
                                      f'Вы можете связаться с работником по корпоративной почте:\n{place[0][5]}\n\n'
                                      f'Время работы сегодня: {str(record[0][0])[:-3]}-{str(record[0][1])[:-3]}\n'
                                      f'Сегодняшние мероприятия: {str(record[0][2])} \n\n'
                                      f'Расписание на пару дней вперёд:\n'
                                      f'{other_days}',
                             reply_markup=kb.Menu)
        Dialog(message)


def location_of_department(message):
    con = psycopg2.connect(**database_connect)
    cursor = con.cursor()
    if "IT" in message.text:
        cursor.execute("SELECT location, department, telephone FROM location_of_departments WHERE department=%s",
                       ["IT"])
        location = cursor.fetchall()
    elif "БУХГАЛТЕРСКИЙ" in message.text:
        cursor.execute("SELECT location, department, telephone FROM location_of_departments WHERE department=%s",
                       ["БУХГАЛТЕРСКИЙ"])
        location = cursor.fetchall()
    elif "ЗАКУПОК" in message.text:
        cursor.execute("SELECT location, department, telephone FROM location_of_departments WHERE department=%s",
                       ["ЗАКУПОК"])
        location = cursor.fetchall()
    elif "КАДРОВ" in message.text:
        cursor.execute("SELECT location, department, telephone FROM location_of_departments WHERE department=%s",
                       ["КАДРОВ"])
        location = cursor.fetchall()
    elif "КАЧЕСТВА" in message.text:
        cursor.execute("SELECT location, department, telephone FROM location_of_departments WHERE department=%s",
                       ["КАЧЕСТВА"])
        location = cursor.fetchall()
    elif "ЛОГИСТИКИ" in message.text:
        cursor.execute("SELECT location, department, telephone FROM location_of_departments WHERE department=%s",
                       ["ЛОГИСТИКИ"])
        location = cursor.fetchall()
    elif "РАЗВИТИЯ" in message.text:
        cursor.execute("SELECT location, department, telephone FROM location_of_departments WHERE department=%s",
                       ["РАЗВИТИЯ"])
        location = cursor.fetchall()
    elif "ТОРГОВЫЙ" in message.text:
        cursor.execute("SELECT location, department, telephone FROM location_of_departments WHERE department=%s",
                       ["ТОРГОВЫЙ"])
        location = cursor.fetchall()
    elif "ФИНАНСОВ" in message.text:
        cursor.execute("SELECT location, department, telephone FROM location_of_departments WHERE department=%s",
                       ["ФИНАНСОВ"])
        location = cursor.fetchall()
    elif "ЮРИДИЧЕСКИЙ" in message.text:
        cursor.execute("SELECT location, department, telephone FROM location_of_departments WHERE department=%s",
                       ["ЮРИДИЧЕСКИЙ"])
        location = cursor.fetchall()
    else:
        location = []
    cursor.close()
    con.close()
    if location == []:
        bot.send_message(message.from_user.id,"Такого отдела не существует, выберете отдел из Меню ниже\n"
                                              "Какой отдел Вас интересует?", reply_markup=kb.department_choice)
        bot.register_next_step_handler(message, location_of_department)
    else:
        first=["IT", "БУХГАЛТЕРСКИЙ", "ТОРГОВЫЙ", "ЮРИДИЧЕСКИЙ"]
        if message.text in first:
            bot.send_message(message.from_user.id, f'{location[0][1]} отдел находится по адресу:\n {location[0][0]}\n'
                                                   f'Телефон для связи: {location[0][2]}',
                             reply_markup=kb.Menu)
        else:
            bot.send_message(message.from_user.id, f'Отдел {location[0][1]} находится по адресу:\n {location[0][0]}\n'
                                                   f'Телефон для связи: {location[0][2]}',
                             reply_markup=kb.Menu)
        Dialog(message)


def quests(message):
    id = get_my_id(message.from_user.id)
    con = psycopg2.connect(**database_connect)
    cursor = con.cursor()
    cursor.execute("SELECT task, done, url_tests, inspection FROM cases WHERE id=%s", [id])
    my_qests = cursor.fetchall()
    cursor.close()
    con.close()
    qests = ''
    qests1 = ''
    if my_qests == []:
        bot.send_message(message.from_user.id,"У Вас нет заданий на текущий момент", reply_markup=kb.Menu)
        Dialog(message)
    else:
        bot.send_message(message.from_user.id, f'Информация по заданиям представлена ниже', reply_markup=kb.Quests)
        item=[]
        for a in range(len(my_qests)):
            if my_qests[a][1] == 'Задание выполнено':
                qests = qests + f'{my_qests[a][0]}          {my_qests[a][3]} \n'
                if len(my_qests[a][2]) > 5:
                    item1 = types.InlineKeyboardButton(text=f'Тест задания {my_qests[a][0]}', url=my_qests[a][2])
                    item.append(item1)
            else:
                qests1 = qests1 + f'{my_qests[a][0]}\n'

        if qests == '':
            qests = 'Выполненные задания отсутствуют'
        if qests1 == '':
            qests1 = 'Не завершённые задания отсутствуют'
        if item != []:
            Tests_url = types.InlineKeyboardMarkup()
            for b in range(len(item)):
                Tests_url.add(item[b])
            bot.send_message(message.from_user.id, f'Ваши задания на текущий период: \n\n'
                                                   f'Выполненные задания: \n'
                                                   f'{qests}\n\n'
                                                   f'В процессе: \n'
                                                   f'{qests1}\n\n',
                             reply_markup=Tests_url)
        else:
            bot.send_message(message.from_user.id, f'Ваши задания на текущий период: \n\n'
                                                   f'Выполненные задания: \n'
                                                   f'{qests}\n\n'
                                                   f'В процессе: \n'
                                                   f'{qests1}\n\n')


        bot.register_next_step_handler(message, fork)


def quest_choice(message):
    id=get_my_id(message.from_user.id)
    con = psycopg2.connect(**database_connect)
    cursor = con.cursor()
    cursor.execute("SELECT task FROM cases WHERE id=%s AND done IS NULL", [id])
    case = cursor.fetchall()
    cursor.close()
    con.close()
    item=[]
    if case == []:
        bot.send_message(message.from_user.id, "У Вас нет заданий на текущий момент", reply_markup=kb.Menu)
        Dialog(message)
    else:
        for a in range(len(case)):
            item1 = types.KeyboardButton(f'{case[a][0]}')
            item.append(item1)
        item0 = types.KeyboardButton("Вернуться")
        Change_Status = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for b in range(len(item)):
            Change_Status.add(item[b])
        Change_Status.add(item0)
        bot.send_message(message.from_user.id, f'Какое из заданий вы выполнили?', reply_markup=Change_Status)
        bot.register_next_step_handler(message, Status_Change)


def Status_Change(message):
    id = get_my_id(message.from_user.id)
    task = message.text
    if task=="Вернуться":
        bot.send_message(message.from_user.id, "Выход в главное меню",
                         reply_markup=kb.Menu)
        Dialog(message)
    else:
        con = psycopg2.connect(**database_connect)
        cursor = con.cursor()
        cursor.execute("UPDATE cases SET done=%s WHERE id=%s AND task=%s ", ["Задание выполнено", id, task])
        con.commit()
        cursor.close()
        con.close()
        bot.send_message(message.from_user.id, "Выполнение отмечено, ожидайте результатов проверки",
                         reply_markup=kb.Menu)
        Dialog(message)


def fork(message):
    if message.text=='Отметить задание как выполненное':
        quest_choice(message)
    else:
        bot.send_message(message.from_user.id, "Выход в главное меню", reply_markup=kb.Menu)
        Dialog(message)




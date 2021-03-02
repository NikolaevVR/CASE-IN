import telebot
import psycopg2
import keyboards as kb
from config import bot_api, database_connect
from datetime import datetime
from datetime import date
from telebot import types
from TelegramBot import *
import time

bot = telebot.TeleBot(bot_api)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    con = psycopg2.connect(**database_connect)
    user_id = message.from_user.id
    cursor = con.cursor()
    cursor.execute("SELECT * FROM employee WHERE telegram=%s",[user_id])
    record = cursor.fetchall()
    if record==[]:
        register(message)
    else:
        bot.send_message(message.from_user.id, "Приветствую", reply_markup=kb.Menu)
        bot.send_message(message.from_user.id, "Можете задать мне вопрос или выбрать интересующий из списка:",
                                                reply_markup=kb.StartQuestions)
        bot.register_next_step_handler(message, Dialog)
    cursor.close()
    con.close()

def register(message):
    bot.send_message(message.from_user.id, "Здравствуйте! Мы не знакомы, давайте познакомимся."
                                           " Введите свою рабочую почту, которую Вам выдали в отделе кадров.")
    bot.register_next_step_handler(message, ask_teleID)

def ask_teleID(message):
    con = psycopg2.connect(**database_connect)
    cursor = con.cursor()
    email=str(message.text)
    cursor.execute("SELECT last_name, first_name FROM employee WHERE email=%s", [str(message.text)])
    record=cursor.fetchall()
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
    cursor.close()
    con.close()


def write_teleID(message,email):
    if message.text=='Да':
        con = psycopg2.connect(**database_connect)
        cursor = con.cursor()
        cursor.execute("UPDATE employee SET telegram=%s WHERE email=%s", [int(message.from_user.id), email])
        con.commit()
        cursor.close()
        con.close()
        bot.send_message(message.from_user.id, "Рад приветствовать Вас в нашей компании!", reply_markup=kb.Menu)
        bot.send_message(message.from_user.id, "Я помогу Вам освоиться и узнать как всё устроено.\n"
                                                "Можете задать мне вопрос или выбрать интересующий из списка:",
                                                reply_markup=kb.StartQuestions)
        bot.register_next_step_handler(message, Dialog)
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

def Dialog(message):
    if message.text == 'Узнать Расписание':
        bot.send_message(message.from_user.id, "Чьё расписание Вы хотите узнать?", reply_markup=kb.Timetable1)
        bot.register_next_step_handler(message, timetable)
    elif message.text == 'Мои задания':
        quests(message)
    elif message.text == 'Найти нужный отдел':
        bot.send_message(message.from_user.id, "Какой отдел Вас интересует?", reply_markup=kb.department_choice)
        bot.register_next_step_handler(message, location_of_department)
    elif message.text == 'Отметить задание как выполненое':
        con = psycopg2.connect(**database_connect)
        cursor = con.cursor()
        cursor.execute("UPDATE cases SET done=%s WHERE id=%s", ["Задание выполнено", get_my_id(message.from_user.id)])
        con.commit()
        cursor.close()
        con.close()
        bot.send_message(message.from_user.id, "Выполнение отмечено, ожидайте результатов", reply_markup=kb.Menu)
        bot.send_message(message.from_user.id, "Можете задать мне вопрос или выбрать интересующий из списка:",
                                                reply_markup=kb.StartQuestions)
        bot.register_next_step_handler(message, Dialog)
    else:
        bot.send_message(message.from_user.id, bright(str(message.text)))
        bot.send_message(message.from_user.id, "Что-то ещё?",
                                                reply_markup=kb.Menu)
        bot.register_next_step_handler(message, Dialog)

def timetable(message):
    if message.text == 'Своё':
        id = get_my_id(message.from_user.id)
        timetable_check(id, message)
    elif message.text == 'Вернуться':
        bot.send_message(message.from_user.id, "Выходим отсюда потихому", reply_markup=kb.Menu)
        bot.send_message(message.from_user.id, "Можете задать мне вопрос или выбрать интересующий из списка:",
                         reply_markup=kb.StartQuestions)
        bot.register_next_step_handler(message, Dialog)
    else:
        bot.send_message(message.from_user.id, "Укажите ФИО интересующего Вас работника")
        bot.register_next_step_handler(message, FIO_check)

def FIO_check(message):
    record = []
    buf=message
    listFIO = message.text.split()
    con = psycopg2.connect(**database_connect)
    cursor = con.cursor()
    if len(listFIO) > 2:
        last_name = listFIO[0]
        first_name = listFIO[1]
        patronymic = listFIO[2]
        cursor.execute("SELECT id FROM employee WHERE first_name=%s AND last_name=%s AND patronymic=%s",
                           [last_name, first_name, patronymic])
        record=cursor.fetchall()
    elif len(listFIO) == 2:
        last_name = listFIO[0]
        first_name = listFIO[1]
        cursor.execute("SELECT id FROM employee WHERE first_name=%s AND last_name=%s", [first_name, last_name])
        record=cursor.fetchall()
    if record==[] or len(listFIO) < 2:
        bot.send_message(message.from_user.id, f'Работника с именем {message.text} не найдено!')
        bot.send_message(message.from_user.id, "Чьё расписание Вы хотите узнать?", reply_markup=kb.Timetable1)
        bot.register_next_step_handler(message, timetable)
    else:
        id = str(record[0][0])
        timetable_check(id, buf)
    cursor.close()
    con.close()


def timetable_check(id, message):
    user_id = message.from_user.id
    now_date = str(datetime.fromtimestamp(int(time.time()))).split()[0]
    now_time = str(datetime.fromtimestamp(int(time.time()))).split()[1]
    con = psycopg2.connect(**database_connect)
    cursor = con.cursor()
    cursor.execute("SELECT last_name, first_name, patronymic, department, workplace, email, position "
                   "FROM employee WHERE id=%s ",
                   [int(id)])
    place=cursor.fetchall()
    cursor.execute("SELECT location FROM location_of_departments WHERE department=%s", [place[0][3]])
    location=cursor.fetchall()
    cursor.execute("SELECT time_start, time_end, appointments FROM timetable WHERE id=%s AND dat=%s", [id, now_date])
    record = cursor.fetchall()
    if record==[]:
        if id==get_my_id(user_id):
            bot.send_message(user_id, f'Вы сегодня не работаете)',
                             reply_markup=kb.Menu)
        else:
            bot.send_message(user_id, f'Сотрудник: {place[0][0]} {place[0][1]} {place[0][2]}\n'
                                      f'Должность: {place[0][6]}\n'
                                      f'Отдел: {place[0][3]} (Рабочее место №{place[0][4]})\n'
                                      f'Находится по адресу: {location[0][0]}\n'
                                      f'Вы можете связаться с работником по корпоративной почте: {place[0][5]}\n'
                                      f'Данного работника уже нет на месте',
                             reply_markup=kb.Menu)
        bot.send_message(user_id, "Можете задать мне вопрос или выбрать интересующий из списка:",
                         reply_markup=kb.StartQuestions)
        bot.register_next_step_handler(message, Dialog)
    else:
        if id==get_my_id(user_id):
            bot.send_message(user_id, f'Время работы сегодня: {str(record[0][0])[:-3]}-{str(record[0][1])[:-3]}\n'
                                      f'Сегодняшние мероприятия: {str(record[0][2])} ',
                             reply_markup=kb.Menu)
        else:
            bot.send_message(user_id, f'Сотрудник: {place[0][0]} {place[0][1]} {place[0][2]}\n'
                                      f'Должность: {place[0][6]}\n'
                                      f'Отдел: {place[0][3]} (Рабочее место №{place[0][4]})\n'
                                      f'Находится по адресу: {location[0][0]}\n'
                                      f'Вы можете связаться с работником по корпоративной почте: {place[0][5]}\n'
                                      f'Время работы сегодня: {str(record[0][0])[:-3]}-{str(record[0][1])[:-3]}\n'
                                      f'Сегодняшние мероприятия: {str(record[0][2])} ',
                             reply_markup=kb.Menu)
        bot.send_message(user_id, "Можете задать мне вопрос или выбрать интересующий из списка:",
                         reply_markup=kb.StartQuestions)
        bot.register_next_step_handler(message, Dialog)
    cursor.close()
    con.close()

def location_of_department(message):
    con = psycopg2.connect(**database_connect)
    cursor = con.cursor()
    if "HR" in message.text:
        cursor.execute("SELECT location, department, telephone FROM location_of_departments WHERE department=%s",
                       ["HR"])
        location = cursor.fetchall()
    elif "IT" in message.text:
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
    if location == []:
        bot.send_message(message.from_user.id,"Такого отдела не существует, выберете отдел из Меню ниже\n"
                                              "Какой отдел Вас интересует?", reply_markup=kb.department_choice )
        bot.register_next_step_handler(message, location_of_department)
    else:
        first=["HR", "IT", "БУХГАЛТЕРСКИЙ", "ТОРГОВЫЙ", "ЮРИДИЧЕСКИЙ"]
        if message.text  in first:
            bot.send_message(message.from_user.id, f'{location[0][1]} отдел находится по адресу:\n {location[0][0]}\n'
                                                   f'Телефон для связи: {location[0][2]}',
                             reply_markup=kb.Menu)
        else:
            bot.send_message(message.from_user.id, f'Отдел {location[0][1]} находится по адресу:\n {location[0][0]}\n'
                                                   f'Телефон для связи: {location[0][2]}',
                             reply_markup=kb.Menu)
        bot.send_message(message.from_user.id, "Можете задать мне вопрос или выбрать интересующий из списка:",
                         reply_markup=kb.StartQuestions)
        bot.register_next_step_handler(message, Dialog)
    cursor.close()
    con.close()

def quests(message):
    id = get_my_id(message.from_user.id)
    con = psycopg2.connect(**database_connect)
    cursor = con.cursor()
    cursor.execute("SELECT task, done, url_tests, inspection FROM cases WHERE id=%s", [id])
    my_qests = cursor.fetchall()
    if my_qests == []:
        bot.send_message(message.from_user.id,"У Вас нет заданий на текущий момент")
        bot.send_message(message.from_user.id, "Можете задать мне вопрос или выбрать интересующий из списка:",
                         reply_markup=kb.StartQuestions)
        bot.register_next_step_handler(message, Dialog)
    else:
        bot.send_message(message.from_user.id, f'Информация по заданию представлена ниже', reply_markup=kb.Menu)
        Tests_url = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton(text='Пройти тестирование', url=f'{my_qests[0][2]}')
        Tests_url.add(item1)
        if my_qests[0][1]=='Задание выполнено':
            bot.send_message(message.from_user.id, f'Ваши задания на текущий период: {my_qests[0][0]} \n'
                                                   f'Статус задания:  {my_qests[0][1]} \n'
                                                   f'Результат: {my_qests[0][3]}\n'
                                                   f'Задание уже выполнено, ожидайте результатов')
        else:
            bot.send_message(message.from_user.id, f'Ваши задания на текущий период: {my_qests[0][0]} \n'
                                                   f'Статус задания:  {my_qests[0][1]} \n'
                                                   f'Результат: {my_qests[0][3]}',
                             reply_markup=Tests_url)
        bot.send_message(message.from_user.id, "Можете задать мне вопрос или выбрать интересующий из списка:",
                         reply_markup=kb.StartQuestions)
        bot.register_next_step_handler(message, Dialog)
    cursor.close()
    con.close()





import telebot
import psycopg2
import keyboards as kb
from config import bot_api, database_connect
from datetime import datetime
from datetime import date
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
        bot.send_message(message.from_user.id, "Рад приветствовать Вас в нашей компании!\n"
                                               "Я помогу Вам освоиться и узнать как всё устроено.\n"
                                                "Можете задать мне вопрос или выбрать интересующий из списка:",
                                                reply_markup=kb.StartQuestions)
        bot.register_next_step_handler(message, Dialog)
    else:
        bot.send_message(message.from_user.id, "Кажется, Вы ввели неправильную почту.\n"
                                               "Введите свою рабочую почту, которую Вам выдали в отделе кадров.")
        bot.register_next_step_handler(message, ask_teleID)


def Dialog(message):
    if message.text == 'Узнать Расписание':
        bot.send_message(message.from_user.id, "Чьё расписание Вы хотите узнать?", reply_markup=kb.Timetable1)
        bot.register_next_step_handler(message, timetable)
    #elif message.text == 'Мои задания':
       # register(message)
    #elif message.text == 'Найти нужный отдел':
       # bot.send_message(message.from_user.id,"Какой отдел Вас интересует?" )
        #bot.register_next_step_handler(message, get_text_messages)
    #elif message.text == 'Нажми если дебил':
        #register(message)
    else:
        bot.send_message(message.from_user.id, "Я ещё не умею общаться")

def timetable(message):
    if message.text == 'Своё':
        con = psycopg2.connect(**database_connect)
        cursor = con.cursor()
        cursor.execute("SELECT id FROM employee WHERE telegram=%s",
                       [int(message.from_user.id)])
        id = str(cursor.fetchall()[0][0])
        print(id)
        cursor.close()
        con.close()
        timetable_check(id, message.from_user.id)
    else:
        bot.send_message(message.from_user.id, "Укажите ФИО интересующего Вас работника")
        bot.register_next_step_handler(message, FIO_check)

def FIO_check(message):
    record = []
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
        print(id)
        timetable_check(id, message.from_user.id)
    cursor.close()
    con.close()


def timetable_check(id, user_id):
    now_date = str(datetime.fromtimestamp(int(time.time()))).split()[0]
    now_time = str(datetime.fromtimestamp(int(time.time()))).split()[1]
    print(now_date)
    print(id)
    con = psycopg2.connect(**database_connect)
    cursor = con.cursor()
    print(id)
    cursor.execute("SELECT last_name, first_name, patronymic, department, workplace, position FROM employee WHERE id=%s ",
                   [int(id)])
    place=cursor.fetchall()
    cursor.execute("SELECT time_start, time_end, appointments FROM timetable WHERE id=%s", [int(id)])
    record = cursor.fetchall()
    print(place)
    print(record)
    if record==[]:
        bot.send_message(user_id, f'Сотрудник: {place[0][0]} {place[0][1]} {place[0][2]}\n'
                                  f'Должность: {place[0][5]}\n'
                                  f'Отдел: {place[0][3]} (Рабочее место №{place[0][4]})\n'
                                  f'Данного работника уже нет на месте')
    else:
        bot.send_message(user_id, f'Сотрудник: {place[0][0]} {place[0][1]} {place[0][2]}\n'
                                  f'Должность: {place[0][5]}\n'
                                  f'Отдел: {place[0][3]} (Рабочее место №{place[0][4]})\n'
                                  f'Время работы сегодня:')





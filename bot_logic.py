import telebot
import psycopg2
import keyboards as kb
from config import bot_api, database_connect

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
        bot.send_message(message.from_user.id, "Можете задать мне вопрос или выбрать интересующий из списка:",
                                                reply_markup=kb.StartQuestions)
        bot.register_next_step_handler(message, StandartAnswers)
        #Добавить менюшку действий????
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
        bot.register_next_step_handler(message, StandartAnswers)
    else:
        bot.send_message(message.from_user.id, "Кажется, Вы ввели неправильную почту.\n"
                                               "Введите свою рабочую почту, которую Вам выдали в отделе кадров.")
        bot.register_next_step_handler(message, ask_teleID)

def StandartAnswers(message):
    if message.text == 'История компании':
        bot.send_message(message.from_user.id, "История компании и ссылка на нужную менюшку сайта")
        bot.send_message(message.from_user.id, "Можете задать мне вопрос или выбрать интересующий из списка:",
                                                reply_markup=kb.StartQuestions)
        bot.register_next_step_handler(message, StandartAnswers)
    elif message.text == 'Корпаративная культура':
        bot.send_message(message.from_user.id, "О Корпаративной культуре и ссылка на нужную менюшку сайта")
        bot.send_message(message.from_user.id, "Можете задать мне вопрос или выбрать интересующий из списка:",
                                                reply_markup=kb.StartQuestions)
        bot.register_next_step_handler(message, StandartAnswers)
    elif message.text == 'Нормативные документы':
        bot.send_message(message.from_user.id, "Нормативные документы или ссылка на страницу с документами")
        bot.send_message(message.from_user.id, "Можете задать мне вопрос или выбрать интересующий из списка:",
                                                reply_markup=kb.StartQuestions)
        bot.register_next_step_handler(message, StandartAnswers)
    else:
        Dialog(message)

def Dialog(message):
    print( f'Пользователь {message.from_user.first_name} сука умный')
    bot.send_message(message.from_user.id, f'{message.from_user.first_name} {message.from_user.last_name}'
                                           f', ты издеваешься?\n'
                                           f'"{message.text}" спрашиваешь ты.\n ДА НЕ ЕБУ Я. Загугли!')
    bot.send_message(message.from_user.id, "Можете задать мне вопрос или выбрать интересующий из списка:",
                     reply_markup=kb.StartQuestions)
    bot.register_next_step_handler(message, StandartAnswers)


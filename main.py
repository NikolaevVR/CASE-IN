from bot_logic import *

if __name__ == '__main__':
    print('Бот запущен')
    bot.polling(none_stop=True, interval=0)
    while True:
        try:
            bot.polling(none_stop=True, interval=1)
        except Exception as e:
            time.sleep(3)
    print(e)





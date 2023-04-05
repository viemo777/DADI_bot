import json
from datetime import datetime
from json import JSONDecodeError

import telebot
from envparse import Env
from telebot.types import Message

from live import TelegramClient

env = Env()
TOKEN = env.str('TOKEN')
ADMIN_CHAT_ID = env.str('ADMIN_CHAT_ID')


# add params to env file
# ADMIN_CHAT_ID = 568869711
# TOKEN = "6083612607:AAEUMjnLkTX8zzlW6VO2KGRdGxC8JU2KLvE"
# TOKEN - берется из @BotFather


class MyBot(telebot.TeleBot):
    def __init__(self, telegram_client: TelegramClient, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.telegram_client = telegram_client


telegram_client = TelegramClient(token=TOKEN, base_url='https://api.telegram.org/bot')
bot = MyBot(token=TOKEN, telegram_client=telegram_client)


@bot.message_handler(commands=['start'])
def start(message: Message):
    with open('users.json', 'r') as f:
        data_from_json = json.load(f)

    user_id = message.from_user.id
    username = message.from_user.username
    if str(user_id) not in data_from_json:
        data_from_json[user_id] = {"username": username}

    with open('users.json', 'w') as f:
        json.dump(data_from_json, f, indent=4, ensure_ascii=False)

    bot.reply_to(message=message, text=str(f'Вы зарегистрированы: {username}. '
                                           f'Ваш ID: {user_id}'))


def handle_messages(message: Message):
    bot.reply_to(message=message, text=f'У тебя красивое имя, {message.text}!')


@bot.message_handler(commands=['say_speech'])
def say_speech(message: Message):
    bot.send_message(message.from_user.id, text='Дoбрый день. Я Vitalii_bot. Назовите ваше имя')
    bot.register_next_step_handler(message, callback=handle_messages)


def create_error_message(err: Exception) -> str:
    return f'Error: {datetime.now()} ::: {err.__class__}: {err}'


while True:
    try:
        bot.polling()
    # inform admin about error
    except JSONDecodeError as err:
        # ADMIN_CHAT_ID - ID of administator's chat for informing about errors.
        # Вариант записи ошибок в админский телеграмм канал ADMIN_CHAT_ID
        bot.send_message(ADMIN_CHAT_ID, text='Ошибка: ' + f'{datetime.now()} ::: {err.__class__}: {err}')
        # альтернативный способ записи ошибки в админсткий телеграмм канал ADMIN_CHAT_ID через post запрос
        bot.telegram_client.post(method='sendMessage',
                                 params={'text': 'Error: ' + f'create_error_message(err)', 'chat_id': ADMIN_CHAT_ID})

# add params to env file
# ADMIN_CHAT_ID = 568869711
# TOKEN = "6083612607:AAEUMjnLkTX8zzlW6VO2KGRdGxC8JU2KLvE"
# TOKEN - берется из @BotFather

import json
from datetime import datetime
from json import JSONDecodeError

import telebot
from envparse import Env
from telebot.types import Message

from DB import UserActioner, PostgresClient
from live import TelegramClient

env = Env()
TOKEN = env.str('TOKEN')
ADMIN_CHAT_ID = env.str('ADMIN_CHAT_ID')

postgres_client = PostgresClient(database="mydb", user='postgres', password='marmak', host='127.0.0.1', port='5432')


class MyBot(telebot.TeleBot):
    def __init__(self, telegram_client: TelegramClient, user_actioner: UserActioner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.telegram_client = telegram_client
        self.user_actioner = user_actioner

    def setup_resources(self):
        self.user_actioner.setup()


telegram_client = TelegramClient(token=TOKEN, base_url='https://api.telegram.org/bot')
user_actioner = UserActioner(db_client=postgres_client)
bot = MyBot(token=TOKEN, telegram_client=telegram_client, user_actioner=user_actioner)
bot.setup_resources()


@bot.message_handler(commands=['start'])
def start(message: Message):
    # секция для записи новых пользователей в json файл.
    with open('users.json', 'r') as f:
        data_from_json = json.load(f)

    user_id = message.from_user.id
    username = message.from_user.username
    if str(user_id) not in data_from_json:
        data_from_json[user_id] = {"username": username}

    with open('users.json', 'w') as f:
        json.dump(data_from_json, f, indent=4, ensure_ascii=False)

    # альтернативная секция для записи новых пользователей в postgres BD.
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id
    create_new_user = None

    if not bot.user_actioner.get_user(user_id=user_id):
        create_new_user = bot.user_actioner.create_user(user_id=user_id, username=username, chat_id=chat_id)
        create_new_user = True

    # бот отвечает в чате на команду /start
    bot.reply_to(message=message, text=f'Вы {"уже" if not create_new_user else ""} зарегистрированы: {username}. '
                                           f'Ваш ID: {user_id}')


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

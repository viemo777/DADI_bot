import json
from datetime import datetime
from json import JSONDecodeError

import telebot
from telebot.types import Message
from envparse import Env

env = Env()
TOKEN = env.str('TOKEN')
ADMIN_ID = env.int('ADMIN_CHAT_ID')
#add params to env file
# ADMIN_ID = 568869711
# TOKEN = "6083612607:AAEUMjnLkTX8zzlW6VO2KGRdGxC8JU2KLvE  "
# TOKEN - берется из @BotFather

bot_client = telebot.TeleBot(token=TOKEN)
@bot_client.message_handler(commands=['start'])
def start(message: Message):

    with open('users.json', 'r') as f:
        data_from_json = json.load(f)

    user_id = message.from_user.id
    username = message.from_user.username
    if str(user_id) not in data_from_json:
        data_from_json[user_id] = {"username": username}

    with open('users.json', 'w') as f:
        json.dump(data_from_json, f, indent=4, ensure_ascii=False)

    bot_client.reply_to(message=message, text=str(f'Вы зарегистрированы: {username}. '        
                                                  f'Ваш ID: {user_id}'))


def handle_messages(message: Message):
    bot_client.reply_to(message=message, text=f'У тебя красивое имя, {message.text}!')
@bot_client.message_handler(commands=['say_speech'])
def say_speech(message: Message):
    bot_client.send_message(message.from_user.id, text='Дoбрый день. Я Vitalii_bot. Назовите ваше имя')
    bot_client.register_next_step_handler(message, callback=handle_messages)

while True:
    try:
        bot_client.polling()
    # inform admin about error
    except JSONDecodeError as err:
        # ADMIN_ID - ID of administator's chat for informing about errors
        bot_client.send_message(ADMIN_ID, text='Ошибка: ' + f'{datetime.now()} ::: {err.__class__}: {err}')

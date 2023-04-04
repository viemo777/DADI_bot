import json

import telebot
from telebot.types import Message

bot_client = telebot.TeleBot(token="6083612607:AAEUMjnLkTX8zzlW6VO2KGRdGxC8JU2KLvE")
ADMIN_ID = 568869711


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

@bot_client.message_handler(commands=['say_speech'])
def say_speech(message: Message):
    bot_client.send_message(chat_id=ADMIN_ID, text=str(f'Добрый день. Меня зовут DADIbot. Спросите меня о чем-нибудь'))


bot_client.polling()

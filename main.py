# add params to env file
# ADMIN_CHAT_ID = 568869711
# TOKEN = "6083612607:AAEUMjnLkTX8zzlW6VO2KGRdGxC8JU2KLvE"
# TOKEN - токен чатбота, берется из @BotFather

import json

from datetime import datetime, date
from json import JSONDecodeError
from logging import StreamHandler, getLogger

import telebot
from envparse import Env
from telebot.types import Message

from ChatGPT import OpenAIWrapper
from DB import UserActioner, PostgresClient
from live import TelegramClient

# секция работы с логгированием
logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel("INFO")
# конец секцим работы с логгированием

env = Env()
TOKEN = env.str('TOKEN')
ADMIN_CHAT_ID = env.str('ADMIN_CHAT_ID')

# работа с БД
postgres_client = PostgresClient(database="mydb", user='postgres', password='marmak', host='127.0.0.1', port='5432')


# конец работа с БД

class MyBot(telebot.TeleBot):
    def __init__(self, telegram_client: TelegramClient, user_actioner: UserActioner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.telegram_client = telegram_client
        self.user_actioner = user_actioner
        self.mode = None

    def setup_resources(self):
        self.user_actioner.setup()

    def setup_mode(self, mode: str):
        self.mode = mode

    def shutdown_resources(self):
        self.user_actioner.shutdown()

    def shutdown(self):
        self.shutdown_resources()


telegram_client = TelegramClient(token=TOKEN, base_url='https://api.telegram.org/bot')
user_actioner = UserActioner(db_client=postgres_client)
bot = MyBot(token=TOKEN, telegram_client=telegram_client, user_actioner=user_actioner)


@bot.message_handler(commands=['start'])
def start(message: Message):
    # секция для записи новых пользователей в json файл.
    # секция работа с json
    with open('users.json', 'r') as f:
        data_from_json = json.load(f)

    user_id = message.from_user.id
    username = message.from_user.username
    if str(user_id) not in data_from_json:
        data_from_json[user_id] = {"username": username}

    with open('users.json', 'w') as f:
        json.dump(data_from_json, f, indent=4, ensure_ascii=False)
    # конец секции работа с json

    # альтернативная секция для записи новых пользователей в postgres BD.
    # работа с БД
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id
    create_new_user = None
    # конец работа с БД

    if not bot.user_actioner.get_user(user_id=user_id):
        create_new_user = bot.user_actioner.create_user(user_id=user_id, username=username, chat_id=chat_id)
        create_new_user = True

    # бот отвечает в чате на команду /start
    bot.reply_to(message=message, text=f'Вы {"уже" if not create_new_user else ""} зарегистрированы: {username}. '
                                       f'Ваш ID: {user_id}')


def handle_messages(message: Message):
    # бот отвечает в чате на команду /report
    bot.reply_to(message=message, text=f'У тебя красивое имя, {message.text}!')
    print(1)


@bot.message_handler(commands=['report'])
def report(message: Message):
    bot.user_actioner.update_last_date(user_id=message.from_user.id, last_date=date.today())
    bot.send_message(message.from_user.id, text='Дoбрый день. Я Vitalii_bot. Назовите ваше имя')
    bot.register_next_step_handler(message, callback=handle_messages)
    bot.setup_mode('report')
    print(2)

def send_respond_vacancies(message: Message):
    # бот отсылает вопрос в ChatGpt API и полученный ответ пишет в чат
    with open('datasets_vacancies_requirements.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        max_caracters = 10000
        for i in range(len(', '.join(lines)) // max_caracters + 1):
            text = ''.join(lines)[i * max_caracters:(i + 1) * max_caracters]
            bot.send_message(message.from_user.id, OpenAIWrapper().get_answer(
                f"Найди в тексте ниже информацию и сообщи мне как в тексте {message.text} \n \n {text}"))
        print(3)

@bot.message_handler(commands=['vacancies'])
def lets_chat(message: Message):
    bot.send_message(message.from_user.id, text='Задай мне вопрос о вакансиях и требованиям к ним')
    bot.register_next_step_handler(message, callback=send_respond_vacancies)
    bot.setup_mode('vacancies')
    print(4)

def send_respond_movies(message: Message):
    # бот отсылает вопрос в ChatGpt API и полученный ответ пишет в чат
    try:
        with open('dataset_movies.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            text = ''.join(lines)
            bot.send_message(message.from_user.id, OpenAIWrapper().get_answer(
                f"Найди в тексте ниже информацию и сообщи мне без изменений {message.text} \n \n {text}"))
            print(5)
    except Exception as e:
        bot.send_message(message.from_user.id, f"В моей базе нет такой информациию Извенить запрос")

@bot.message_handler(commands=['movies'])
def lets_chat(message: Message):
    bot.send_message(message.from_user.id, text='Задай мне вопрос о фильмах 2022 года')
    bot.register_next_step_handler(message, callback=send_respond_movies)
    bot.setup_mode('movies')
    print(6)

def send_respond(message: Message):
    # бот отсылает вопрос в ChatGpt API и полученный ответ пишет в чат
    openAIWrapper = OpenAIWrapper()
    response = openAIWrapper.get_answer(message.text)
    bot.send_message(message.from_user.id, text=response)
    print(7)

@bot.message_handler(commands=['lets_chat'])
def lets_chat(message: Message):
    bot.send_message(message.from_user.id, text='Задай мне вопрос на любую тему')
    bot.register_next_step_handler(message, callback=send_respond)
    bot.setup_mode('lets_chat')
    print(8)

# бот отвечает на любое сообщение в чате, кроме указанных выше команд
@bot.message_handler(func=lambda message: True)
def echo_all(message: Message):
    print(9)
    if bot.mode == 'vacancies':
        send_respond_vacancies(message)

    elif bot.mode == 'movies':
          send_respond_movies(message)

def create_error_message(err: Exception) -> str:
    return f'Error: {datetime.now()} ::: {err.__class__}: {err}'


while True:
    try:
        bot.setup_resources()
        bot.polling()
    # inform admin about error
    except JSONDecodeError as err:
        # секция работы с логгированием
        error_message = create_error_message(err)
        logger.error(error_message)
        # конец секцим работы с логгированием

        # ADMIN_CHAT_ID - ID of administator's chat for informing about errors.
        # Вариант записи ошибок в админский телеграмм канал ADMIN_CHAT_ID
        bot.send_message(ADMIN_CHAT_ID, text='Ошибка: ' + f'{datetime.now()} ::: {err.__class__}: {err}')
        # альтернативный способ записи ошибки в админсткий телеграмм канал ADMIN_CHAT_ID через post запрос
        bot.telegram_client.post(method='sendMessage',
                                 params={'text': 'Error: ' + f'error_message', 'chat_id': ADMIN_CHAT_ID})
        bot.shutdown()

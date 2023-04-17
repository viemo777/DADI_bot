# add params to env file
# ADMIN_CHAT_ID = 568869711
# TOKEN - токен чатбота, берется из @BotFather

import json
import time

from datetime import datetime, date
from json import JSONDecodeError
from logging import StreamHandler, getLogger

import redis as redis
import telebot
from envparse import Env
from telebot.types import Message

from ChatGPT import OpenAIWrapper
from DB import UserActioner, PostgresClient
from live import TelegramClient

from telebot import types

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
print('bot created')


@bot.message_handler(commands=['start'])
def start(message: Message):
    print('handle_start')
    # Секция для записи новых пользователей в json файл.
    # Записывается любой пользователь, кто вошел в бот
    with open('users.json', 'r') as f:
        data_from_json = json.load(f)

    user_id = message.from_user.id
    username = message.from_user.username
    if str(user_id) not in data_from_json:
        data_from_json[user_id] = {"username": username}

    with open('users.json', 'w') as f:
        json.dump(data_from_json, f, indent=4, ensure_ascii=False)
    # конец секции для записи новых пользователей в json файл.

    verify_user(message=message, from_start=True)


@bot.message_handler(commands=['menu'])
def menu(message: Message):
    print('handle_menu')
    if not verify_user(message=message):
        exit()

    menu_keyboard_manager(message=message, menu="main_menu")


# бот отвечает на любое сообщение в чате, кроме указанных выше команд
@bot.message_handler(func=lambda message: True)
def echo_all(message: Message):
    print(9)
    if not verify_user(message=message):
        exit()

    if bot.mode == 'vacancies':
        send_respond_vacancies(message)

    elif bot.mode == 'movies':
        send_respond_movies(message)

    elif bot.mode == 'say_speech':

        send_respond_from_gpt(message)
    else:
        pass


def menu_keyboard_manager(message: Message = None, menu = 1):
    print(14)

    if menu == "training_list":
        markup = types.InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(types.InlineKeyboardButton("Тренинг 1", callback_data="training_1"),
                   types.InlineKeyboardButton("Тренинг 2", callback_data="training_2"),
                   types.InlineKeyboardButton("Тренинг 3", callback_data="training_3"))
        bot.send_message(message.chat.id, "Ниже представлен список ваших незавершенных тренингов. \n"
                                          "Для прохождения выберите любой", reply_markup=markup)
    if menu == "my_results":
        bot.send_message(message.chat.id, "Ваш коэффициент эффективности за текущий месяц = 0,96. \n"
                                          "Ваша эффективность выше среднего по компании на 4% \n"
                                          "Количество пройденных тренингов за текущий месяц = 3. \n"
                                          "Количество непройденных тренингов = 5. \n")

        markup = types.InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(types.InlineKeyboardButton("Меню", callback_data="main_menu"),
                   types.InlineKeyboardButton("Мои тренинги", callback_data="my_trainings"))
        bot.send_message(message.chat.id, "Выберите следующее действие", reply_markup=markup)
    elif menu == "main_menu":
        markup = types.InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(types.InlineKeyboardButton("👨‍🏫 Мои тренинги", callback_data="training_list"),
                   types.InlineKeyboardButton("🥇 Мои результаты", callback_data="my_results"),
                   types.InlineKeyboardButton("🌐 Открыть в WEB", url="https://www.google.com/"))
        bot.send_message(message.chat.id, "Выберите действие", reply_markup=markup)

    elif menu == 10:
        markup = types.InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(types.InlineKeyboardButton("Yes", callback_data="cb_yes"),
                   types.InlineKeyboardButton("No", callback_data="cb_no"))
        bot.send_message(message.chat.id, "Выберите действие", reply_markup=markup)
    elif menu == 2:
        id = message.text.replace("/send ", "")
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Sticker', callback_data='sticker'),
                   types.InlineKeyboardButton('Document', callback_data='document'))
        markup.add(types.InlineKeyboardButton('Photo', callback_data='photo'),
                   types.InlineKeyboardButton('Video', callback_data='video'))
        markup.add(types.InlineKeyboardButton('Audio', callback_data='Audio'))
     #   redis.hset('file_id', message.chat.id, '{}'.format(id))
        bot.send_message(message.chat.id, 'Select _One_ of these `Items.:D` \n\n (Note: GIFs are Documents)',
                         reply_markup=markup, parse_mode="Markdown")
    elif menu == 3:
        cid = message.chat.id
        markup = types.InlineKeyboardMarkup()
        b = types.InlineKeyboardButton("Help", callback_data='help')
        c = types.InlineKeyboardButton("About", callback_data='amir')
        markup.add(b, c)
        nn = types.InlineKeyboardButton("Inline Mode", switch_inline_query='')
        oo = types.InlineKeyboardButton("Channel", url='https://telegram.me/offlineteam')
        markup.add(nn, oo)
        id = message.from_user.id
        #redis.sadd('memberspy', id)
        bot.send_message(cid, "Hi \n\n Welcome To TweenRoBOT \n\n Please Choose One :)", disable_notification=True,
                         reply_markup=markup)

    elif menu == 4:
        bot.send_chat_action(message.chat.id, 'typing')
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton('戳这里！', url = 'https://t.me/yahahaabot')
        markup.add(btn)
        msg_id = bot.send_message(chat_id=message.chat.id, text=u'为了防止刷屏，请在私聊中使用此命令哦～',reply_markup=markup).message_id
        time.sleep(5)
        bot.delete_message(message.chat.id,msg_id)

    elif menu == 5:
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(text='English', callback_data='chooselang:en'),
                   types.InlineKeyboardButton(text='فارسی', callback_data='chooselang:fa'))
        bot.send_message(message.chat.id, "Hi \n\n Welcome To TweenRoBOT \n\n Please Choose One :)", disable_notification=True,
                         reply_markup=markup)
    # --- Multi Lang ---
    elif menu == 6:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Google", url="http://www.google.com"))
        markup.add(types.InlineKeyboardButton("Yahoo", url="http://www.yahoo.com"))
        iq = types.InlineQueryResultCachedPhoto('aaa', 'Fileid', title='Title', reply_markup=markup)
        json_str = iq.to_json()
        assert 'aa' in json_str
        assert 'Fileid' in json_str
        assert 'Title' in json_str
        assert 'caption' not in json_str
        assert 'reply_markup' in json_str
        bot.send_message(message.chat.id, "Hi \n\n Welcome To TweenRoBOT \n\n Please Choose One :)", disable_notification=True,
                 reply_markup=markup)
    elif menu == 7:
        text = 'CI Test Message'
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Google", url="http://www.google.com"))
        markup.add(types.InlineKeyboardButton("Yahoo", url="http://www.yahoo.com"))
        ret_msg = bot.send_message(message.from_user.id, text, disable_notification=True, reply_markup=markup)
        assert ret_msg.message_id

    elif menu == 8:
        text = 'CI Test Message'
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Google", url="http://www.google.com"))
        markup.add(types.InlineKeyboardButton("Yahoo", url="http://www.yahoo.com"))
        ret_msg = bot.send_message(message.from_user.id, text, disable_notification=True, reply_markup=markup)
        markup.add(types.InlineKeyboardButton("Google2", url="http://www.google.com"))
        markup.add(types.InlineKeyboardButton("Yahoo2", url="http://www.yahoo.com"))
        new_msg = bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=ret_msg.message_id, reply_markup=markup)
        assert new_msg.message_id

    elif menu == 9:
        markup = types.InlineKeyboardMarkup()
        if message.text.count(' ') != 1:
            bot.send_chat_action(message.chat.id, 'typing')
            bot.send_message(message.chat.id, '输入格式有误，例：`/yyets 神盾局特工`', parse_mode='Markdown')
            return
        bot.send_chat_action(message.chat.id, 'typing')
        season_count, msg = message.text.split(' ')[1]
        if season_count == 0:
            bot.send_message(message.chat.id, msg)
            return
        elif season_count == 255:
            bot.send_message(message.chat.id, msg)
            return
        for button in range(1, season_count + 1):
            markup.add(types.InlineKeyboardButton
                       ("第%s季" % button,
                        callback_data='%s %s' % (message.text.split(' ')[1], button)))
        bot.send_message(message.chat.id, "你想看第几季呢？请点击选择", reply_markup=markup)

    elif menu == 10:
        dict = {"Name": "John", "Language": "Python", "API": "pyTelegramBotAPI"}

        buttons = []

        for key, value in dict.items():
            buttons.append(
                [types.InlineKeyboardButton(text=key, url='google.com')]
            )
        keyboard = types.InlineKeyboardMarkup(buttons)
        bot.send_message(message.from_user.id, text='f', reply_markup=keyboard)

def keyboard_manager(action: str):
    print(13)

    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)  # Connect the keyboard
    if action == 'add_phone':
        button_phone = types.KeyboardButton(text="Отправь свой номер",
                                            request_contact=True)  # Specify the name of the button that the user will see
        keyboard.add(button_phone)  # Add this button

    return keyboard


def verify_user(message: Message, from_start=False):
    print('verify_user')
    # работа с БД Postgres
    # регистрируются только пользователи, если они отправили номер телефона и этот номер есть в белом списке
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id

    with open('whitelist_phone_numbers.txt', 'r') as file:
        # read all content of a file
        content = file.read()

    user = bot.user_actioner.get_user(user_id=user_id)

    if not user:
        print('verify_user1')

        keyboard = keyboard_manager(action='add_phone')
        bot.send_message(message.from_user.id,
                         text=f'Это закрытый бот. Необходима проверка по номеру телефона: {username}. '
                              f'Ваш ID: {user_id}. '
                              f'Для проверки права доступа к боту воспользуйтесь функцией "Отправь '
                              f'свой номер".'
                         , reply_markup=keyboard)
    elif user and user[4] and user[4] in content:
        print('verify_user2')
        print(from_start)
        if from_start:
            # бот отвечает в чате на команду /start
            bot.reply_to(message=message, text=f'Вы уже зарегистрированы: {username}. '
                                               f'Ваш ID: {user_id}')
        return True

    else:  # когда user есть в базе, но его номер телефона не в белом списке
        print('verify_user3')
        # бот отвечает в чате на команду /start
        bot.reply_to(message=message,
                     text=f'У Вас нет права доступа к этому боту. Обратитесь к HR менеджеру Вашей организации. '
                          f'Ваш ID: {user_id}')
    # конец работа с БД

    return False

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):

    print(call.data)

    if call.data=="training_list":
        bot.answer_callback_query(callback_query_id=call.id,
                              show_alert=False,
                              text="You Clicked " + call.data)
        delete_message = bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        menu_keyboard_manager(message=call.message, menu="training_list")
    elif call.data=="my_results":
        bot.answer_callback_query(callback_query_id=call.id,
                              show_alert=False,
                              text="You Clicked " + call.data)
        delete_message = bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        menu_keyboard_manager(message=call.message, menu="my_results")
    elif call.data=="main_menu":
        bot.answer_callback_query(callback_query_id=call.id,
                              show_alert=False,
                              text="You Clicked " + call.data)
        delete_message = bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        menu_keyboard_manager(message=call.message, menu="main_menu")


def handle_report(message: Message):
    print('report')
    # бот отвечает в чате на команду /report
    bot.reply_to(message=message, text=f'У тебя красивое имя, {message.text}!')


@bot.message_handler(commands=['report'])
def report(message: Message):
    print('handle_report')
    if not verify_user(message=message):
        exit()

    bot.user_actioner.update_last_date(user_id=message.from_utser.id, last_date=date.today())
    bot.send_message(message.from_user.id, text='Дoбрый день. Я бот системы Доктрина. Представьтесь, пож-та')
    bot.register_next_step_handler(message, callback=handle_report)
    bot.setup_mode('report')


def send_respond_vacancies(message: Message):
    print('send_respond_vacancies')
    # бот отсылает вопрос в ChatGpt API и полученный ответ пишет в чат
    with open('datasets_vacancies_requirements.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        max_caracters = 10000
        for i in range(len(', '.join(lines)) // max_caracters + 1):
            text = ''.join(lines)[i * max_caracters:(i + 1) * max_caracters]
            bot.send_message(message.from_user.id, OpenAIWrapper().get_answer(
                f"Найди в тексте ниже информацию о {message.text} \n \n {text}"))


@bot.message_handler(commands=['vacancies'])
def vacancies(message: Message):
    print('handle_vacancies')
    if not verify_user(message=message):
        exit()

    bot.send_message(message.from_user.id, text='Задай мне вопрос о вакансиях и требованиям к ним')
    bot.register_next_step_handler(message, callback=send_respond_vacancies)
    bot.setup_mode('vacancies')


def send_respond_movies(message: Message):
    print('send_respond_movies')
    # бот отсылает вопрос в ChatGpt API и полученный ответ пишет в чат
    try:
        with open('dataset_movies.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            text = ''.join(lines)
            bot.send_message(message.from_user.id, OpenAIWrapper().get_answer(
                f"Найди в тексте ниже информацию о {message.text} \n \n {text}"))

    except Exception as e:
        bot.send_message(message.from_user.id, f"В моей базе нет такой информацию. Изменить запрос")


@bot.message_handler(commands=['movies'])
def movies(message: Message):
    print('handle_movies')
    if not verify_user(message=message):
        exit()

    bot.send_message(message.from_user.id, text='Задай мне вопрос о фильмах 2022 года')
    bot.register_next_step_handler(message, callback=send_respond_movies)
    bot.setup_mode('movies')


def send_respond_from_gpt(message: Message):
    print('send_respond_lets_chat')
    # бот отсылает вопрос в ChatGpt API и полученный ответ пишет в чат
    openAIWrapper = OpenAIWrapper()
    response = openAIWrapper.get_answer(message.text)
    bot.send_message(message.from_user.id, text=response)


@bot.message_handler(commands=['lets_chat'])
def lets_chat(message: Message):
    print('handle_lets_chat')
    if not verify_user(message=message):
        exit()

    bot.send_message(message.from_user.id, text='Задай мне вопрос на любую тему')
    bot.register_next_step_handler(message, callback=send_respond_from_gpt)
    bot.setup_mode('lets_chat')


# секция для запроса у пользователя номера телефона
@bot.message_handler(commands=['number'])  # Announced a branch to work on the <strong> number </strong> command
def phone(message):
    print('handle_number')
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)  # Connect the keyboard
    button_phone = types.KeyboardButton(text="Отправь свой номер",
                                        request_contact=True)  # Specify the name of the button that the user will see
    keyboard.add(button_phone)  # Add this button
    bot.send_message(message.chat.id, 'Отправьте свой номер телефона для проверки права доступа к боту',
                     reply_markup=keyboard)  # Duplicate with a message that the user will now send his phone number to the bot (just in case, but this is not necessary)


# управление видимостью кнопок клавиатуры, зависит от прав пользователя
def change_keyboard_buttons(message: Message, text: str):
    print('change_keyboard_buttons')
    a = types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, text, reply_markup=a)


@bot.message_handler(content_types=[
    'contact'])  # Announced a branch in which we prescribe logic in case the user decides to send a phone number :)
def contact(message):
    print('handle_contact')
    if message.contact is not None:  # If the sent object <strong> contact </strong> is not zero

        # hire you must verify the phone number in white list phone numbers
        # if phone number in white list phone numbers, then you send message to user and remove button from keyboard
        content = None
        with open('whitelist_phone_numbers.txt', 'r') as file:
            # read all content of a file
            content = file.read()

        user_id = message.from_user.id
        username = message.from_user.username
        chat_id = message.chat.id

        if message.contact.phone_number in content:
            create_new_user = bot.user_actioner.create_user(user_id=user_id, username=username, chat_id=chat_id,
                                                            phone=message.contact.phone_number)

            # bot.send_message(message.chat.id, 'Ваш номер телефона принят. Добро пожаловать в бота Доктрина.')
            change_keyboard_buttons(message, 'Ваш номер телефона принят. Добро пожаловать в бот Doctrina.\n'
                                             'Воспользуйтесь меню для получения доступа к функциям бота.')
        else:
            # bot.send_message(message.chat.id, 'Ваш номер телефона не принят. Доступ к боту запрещен.')
            change_keyboard_buttons(message, 'Ваш номер телефона не принят. Доступ к боту запрещен.')


# конец секции для запроса у пользователя номера телефона


def create_error_message(err: Exception) -> str:
    return f'Error: {datetime.now()} ::: {err.__class__}: {err}'


while True:
    try:
        bot.setup_resources()
        bot.polling(none_stop=True, timeout=123)
        #bot.infinity_polling(timeout=10, long_polling_timeout=5)
        print(f'restart bot {datetime.now()}')
    # inform admin about error
    except JSONDecodeError as err:
        # секция работы с логгированием

        error_message = create_error_message(err)
        logger.error(error_message)
        # конец секцим работы с логгированием
        print(f'{error_message} {datetime.now()}')
        # ADMIN_CHAT_ID - ID of administator's chat for informing about errors.
        # Вариант записи ошибок в админский телеграмм канал ADMIN_CHAT_ID
        bot.send_message(ADMIN_CHAT_ID, text='Ошибка: ' + f'{datetime.now()} ::: {err.__class__}: {err}')
        # альтернативный способ записи ошибки в админсткий телеграмм канал ADMIN_CHAT_ID через post запрос
        bot.telegram_client.post(method='sendMessage',
                                 params={'text': f'Error: {error_message}', 'chat_id': ADMIN_CHAT_ID})
        bot.shutdown()

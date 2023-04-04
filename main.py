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
    if user_id not in data_from_json:
        data_from_json.append()

    with open('users.json', 'ц') as f:
        json.dump(data_from_json, f, indent=4, ensure_ascii=False


    bot_client.reply_to(message=message, text=str(message.chat.id))


bot_client.polling()
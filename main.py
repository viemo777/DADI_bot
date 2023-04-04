import telebot
from telebot.types import Message

bot_client = telebot.TeleBot(token="6083612607:AAEUMjnLkTX8zzlW6VO2KGRdGxC8JU2KLvE")
ADMIN_ID = 568869711

@bot_client.message_handler(commands=['start'])
def start(message: Message):
    bot_client.reply_to(message, "Hello, I am a bot")


bot_client.polling()

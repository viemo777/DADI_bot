# секция работы с логгированием
from logging import getLogger, StreamHandler

from envparse import Env
from datetime import date

from DB import PostgresClient
from live import TelegramClient

logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel("INFO")
# конец секцим работы с логгированием

env = Env()
TOKEN = env.str('TOKEN')

class Reminder:
    GET_TASKS_QUERY = """
        SELECT chat_id FROM users WHERE last_updated_date IS NULL OR last_updated_date < date('now')
        """

    def __init__(self, telegram_client: TelegramClient, postgress_client: PostgresClient):
        self.telegram_client = telegram_client
        self.postgress_client = postgress_client
        self.setted_up = False

    def setup(self):
        self.postgress_client.create_connection()
        self.setted_up = True

    def shutdown(self):
        self.postgress_client.close_connection()
        self.setted_up = False

    def notify(self, chat_ids: list):
        for chat_id in chat_ids:
            res = self.telegram_client.post(method='sendMessage', params={'chat_id': chat_id, 'text': 'Вы сегодня не отчитались. Завершите'})
            logger.info(res)

    def __call__(self, *args, **kwargs):
        if not self.setted_up:
            logger.error('Reminder is not setted up')
            return
        self.execute()

    def execute(self):
        chat_ids = self.postgress_client.execute_select_command(self.GET_TASKS_QUERY)
        if chat_ids:
            self.notify(chat_ids=[tuple_from_db[0] for tuple_from_db in chat_ids])

if __name__ == '__main__':
    telegram_client = TelegramClient(TOKEN, base_url='https://api.telegram.org/bot')
    postgress_client = PostgresClient(database="mydb", user='postgres', password='marmak', host='127.0.0.1', port='5432')
    reminder = Reminder(telegram_client, postgress_client)
    reminder.setup()
    reminder.execute()

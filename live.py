import requests


class TelegramClient:
    def __init__(self, token: str, base_url: str):
        self.token = token
        self.base_url = base_url

    def prepare_url(self, method: str):
        result_url = f'{self.base_url}{self.token}/'
        if method is not None:
            result_url += method
        return result_url

    def post(self, method: str = None, params: dict = None, body: dict = None):
        url = self.prepare_url(method=method)
        response = requests.post(url, params=params, data=body)
        return response.json()


if __name__ == '__main__':
    TOKEN = "6083612607:AAEUMjnLkTX8zzlW6VO2KGRdGxC8JU2KLvE"
    ADMIN_CHAT_ID = 568869711

    telegram_client = TelegramClient(token=TOKEN, base_url='https://api.telegram.org/bot')
    my_params = {'chat_id': ADMIN_CHAT_ID, 'text': 'Hello, world!'}
    print(telegram_client.post(method='sendMessage', params=my_params))

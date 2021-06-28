import telegram
from fileinput import FileInput


class Telegram():
    def __init__(self, token='', client_id=''):
        self.bot = telegram.Bot(token)
        self.client_id = str(client_id)

    def send(self, message='') -> str:
        try:
            if message.startswith('file:'):
                file = message.replace('file:', '')
                self.bot.send_photo(chat_id=self.client_id, photo=open(file, 'rb'))
            else:
                self.bot.send_message(chat_id=self.client_id, text=message)

        except Exception as err:
            print(err)
            return ''


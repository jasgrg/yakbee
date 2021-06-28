
import telegram
from telegram.ext import Updater, CommandHandler, CallbackContext
from os import walk

class Telegram():
    def __init__(self, token='', client_id=''):
        self.bot = telegram.Bot(token)
        self.client_id = str(client_id)

        updater = Updater(token)
        def upload_graph(update: telegram.Update, context: CallbackContext):
            curr = update.message.text.split(' ')[1]
            for (dirpath, dirnames, filenames) in walk('graphs'):
                for filename in filenames:
                    if str(filename).lower().startswith(curr):
                        self.bot.send_photo(chat_id=self.client_id, photo=open(f'graphs/{filename}', 'rb'))
        updater.dispatcher.add_handler(CommandHandler('g', upload_graph))
        updater.start_polling()


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



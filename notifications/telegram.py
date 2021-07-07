import telegram
from telegram.ext import Updater, CommandHandler, CallbackContext
from os import walk


class Telegram():
    def __init__(self, token='', client_id='', poll=False):
        self.bot = telegram.Bot(token)
        self.client_id = str(client_id)
        self.amounts = {}

        if poll:
            updater = Updater(token)
            def upload_graph(update: telegram.Update, context: CallbackContext):
                curr = update.message.text.split(' ')[1]
                for (dirpath, dirnames, filenames) in walk('graphs'):
                    for filename in filenames:
                        if str(filename).lower().startswith(curr):
                            self.bot.send_photo(chat_id=self.client_id, photo=open(f'graphs/{filename}', 'rb'), caption=filename)
            updater.dispatcher.add_handler(CommandHandler('g', upload_graph))

            def upload_traders(update: telegram.Update, context: CallbackContext):
                for (dirpath, dirnames, filenames) in walk('graphs'):
                    for filename in filenames:
                        if str(filename).lower().endswith('_trades.png'):
                            self.bot.send_photo(chat_id=self.client_id, photo=open(f'graphs/{filename}', 'rb'), caption=filename)

            updater.dispatcher.add_handler(CommandHandler('t', upload_traders))

            def post_amounts(update: telegram.Update, context: CallbackContext):
                for key in self.amounts:
                    self.send(f'{key} : {self.amounts[key]["base_amount"]} ' +
                                    f'{self.amounts[key]["base_currency"]} | ' +
                                    f'{self.amounts[key]["quote_amount"]} ' +
                                    f'{self.amounts[key]["quote_currency"]} | ' +
                                    f'{self.amounts[key]["total"]}')
            updater.dispatcher.add_handler(CommandHandler('a', post_amounts))

            updater.start_polling()

    def send(self, message='') -> str:
        try:
            if isinstance(message, dict):
                self.amounts[message['alias']] = message
            elif message.startswith('file:'):
                file = message.replace('file:', '')
                self.bot.send_photo(chat_id=self.client_id, photo=open(file, 'rb'))
            else:
                self.bot.send_message(chat_id=self.client_id, text=message)

        except Exception as err:
            print(err)
            return ''

import time
import sched
from models.config import Config
from traders.trader import Trader
from notifications.notification_service import NotificationService
import traceback


class TradeManager():
    def __init__(self, config: Config, log, notification: NotificationService):
        self.log = log
        self.notify_service = notification
        self.config = config
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.traders = []

    def run(self):
        self.traders = self.create_traders(self.config.config)
        self.notify_service.notify(f'Yakbee running with {len(self.traders)} traders')
        self.scheduler.enter(5, 1, self.main_loop, ())
        self.scheduler.run()

    def main_loop(self):
        for trader in self.traders:
            try:
                trader.calculate_and_trade(time.time())
            except Exception as ex:
                self.log.error(traceback.format_exc())
                self.notify_service.notify(str(ex))
        self.scheduler.enter(5, 1, self.main_loop, ())

    def create_traders(self, config: Config) -> []:
        traders = []
        for t in config['traders']:
            traders.append(Trader(t, self.log, self.notify_service))

        return traders

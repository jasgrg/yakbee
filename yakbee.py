from log.logservice import Log
from notifications.telegram import Telegram
from notifications.notification_service import NotificationService
from models.config import Config
from traders.trade_manager import TradeManager
from sim.sim_trade_manager import SimTradeManager
import traceback

def main():


    try:

        config = Config()
        log = Log(config)

        ns = NotificationService()

        if 'telegram' in config.config:
            telegram = Telegram(config.config['telegram']['token'], config.config['telegram']['client_id'], poll=True)
            ns.add_handler(telegram.send)

        log.debug("Starting")
        if 'sim' in config.config and config.config['sim']['simulation']:
            trade_manager = SimTradeManager(config, log)
        else:
            trade_manager = TradeManager(config, log, ns)

        trade_manager.run()
    except KeyboardInterrupt:
        log.debug('Received shutdown signal')

    except Exception as ex:
        log.error(str(traceback.format_exc()))

if __name__ == '__main__':
    main()
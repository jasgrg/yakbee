from log.logservice import Log
from models.config import Config
from traders.trade_manager import TradeManager
from sim.sim_trade_manager import SimTradeManager
import traceback

def main():


    try:

        config = Config()
        log = Log(config)
        log.debug("Starting")
        if 'sim' in config.config and config.config['sim']['simulation']:
            trade_manager = SimTradeManager(config, log)
        else:
            trade_manager = TradeManager(config, log)

        trade_manager.run()
    except KeyboardInterrupt:
        log.debug('Received shutdown signal')

    except Exception as ex:
        log.error(str(traceback.format_exc()))


main()
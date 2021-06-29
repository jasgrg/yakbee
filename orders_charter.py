from log.logservice import Log
from models.config import Config
from traders.trader import Trader
import traceback
from datetime import datetime, timedelta
from traders.signals.signal_type import SignalAction
import pandas as pd
import pytz

def main():


    try:

        config = Config()
        log = Log(config)
        log.debug("Starting")

        for t in config.config['traders']:
            t['live'] = 1
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(seconds=1600*t['config']['granularity'])

            trader = Trader(t, log)
            orders = trader.exchange.get_filled_orders()
            data = trader.exchange.get_historic_data(trader.config.granularity, start_date, end_date)
            trader.trades_to_render = [{
                'time': pd.to_datetime(o['created_at']),
                'close': float(o['price']),
                'action': SignalAction.BUY if o['side'] == 'buy' else SignalAction.SELL
            } for o in orders]
            trader.trades_to_render = [t for t in trader.trades_to_render if t['time'] > pytz.UTC.localize(start_date)]
            trader.render(data)


    except Exception as ex:
        log.error(str(traceback.format_exc()))


main()
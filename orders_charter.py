from log.logservice import Log
from models.config import Config
from traders.trader import Trader
import traceback
from datetime import datetime, timedelta
from traders.signals.signal_action import SignalAction
import pandas as pd
import pytz

def chart_orders():
    try:

        config = Config()
        log = Log(config)
        log.debug("Starting")

        for t in config.config['traders']:
            t['live'] = 1
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(seconds=1600*t['config']['granularity'])

            trader = Trader(t, log)

            data = trader.exchange.get_historic_data(trader.config.granularity, start_date, end_date)
            trader.trades_to_render = [t for t in trader.trades_to_render if t['time'] > pytz.UTC.localize(start_date)]
            trader.render(data)

    except Exception as ex:
        log.error(str(traceback.format_exc()))

if __name__ == '__main__':
    chart_orders()
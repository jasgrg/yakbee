from traders.signals.signal_type import SignalAction
from traders.trader import Trader
from datetime import datetime
import time

class SimTrader(Trader):
    def __init__(self, config, log, start_time, end_time):
        config['live'] = 0
        super().__init__(config, log)
        self.historical_data = self.exchange.get_historic_data(self.config.granularity, start_time, end_time)
        self.current_time = None
        self.trades = []

    def get_historical_data(self, current_time):
        self.current_time = time.ctime(current_time)
        return self.historical_data.loc[self.historical_data['epoch'] <= current_time].copy()


    def trade(self, action: SignalAction, close: float):
        if super().trade(action, close):
            base_amt = self.exchange.get_available_amount(self.config.base_currency)
            quote_amt = self.exchange.get_available_amount(self.config.quote_currency)

            self.trades.append({
                "date": self.current_time,
                "action": action,
                "close": close,
                "base_amt": base_amt,
                "quote_amt": quote_amt
            })
            return True
        return False


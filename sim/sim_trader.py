from traders.signals.signal_action import SignalAction
from traders.trader import Trader
from datetime import datetime, timezone
from traders.exchanges.dummy_exchange import DummyExchange

class SimTrader(Trader):
    def __init__(self, config, log, start_date, end_time, data_file):
        config['live'] = 0
        self.start_date = start_date
        self.data_file = data_file

        super().__init__(config, log)
        self.render_after_calc = False
        self.historical_data = self.exchange.get_historic_data(self.config.granularity, start_date, end_time)
        self.current_time = None


    def get_historical_data(self, current_time):
        self.current_time = datetime.fromtimestamp(current_time).astimezone(timezone.utc)
        return self.historical_data.loc[self.historical_data['epoch'] <= current_time].copy()

    def trade(self, action: SignalAction, close: float):
        if super().trade(action, close):
            self.exchange.orders[0]['date'] = self.current_time
            return True
        return False

    def get_exchange(self, exchange):
        x = self._get_base_exchange(exchange)
        return DummyExchange(x, self.config, self.log, self.start_date, self.data_file)

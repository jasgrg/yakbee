from traders.signals.signal_action import SignalAction
from traders.trader import Trader
from datetime import datetime
from helpers import datetime_helpers

class SimTrader(Trader):
    def __init__(self, config, log, start_time, end_time):
        config['live'] = 0
        super().__init__(config, log)
        self.render_after_calc = False
        self.historical_data = self.exchange.get_historic_data(self.config.granularity, start_time, end_time)
        self.current_time = None

    def get_historical_data(self, current_time):
        self.current_time = datetime.fromtimestamp(current_time, tz=datetime_helpers.LOCAL_TIMEZONE)
        return self.historical_data.loc[self.historical_data['epoch'] <= current_time].copy()


    def trade(self, action: SignalAction, close: float):
        if super().trade(action, close):
            self.exchange.orders[-1]['date'] = self.current_time
            return True
        return False


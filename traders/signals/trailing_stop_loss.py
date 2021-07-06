from traders.signals.signal_action import SignalAction
from traders.signals.signal import Signal
from numpy import maximum
import matplotlib.pyplot as plt


class TrailingStopLoss(Signal):
    def __init__(self, log, alias, config=None):
        super().__init__()
        self.log = log
        self.alias = alias

        if config is not None:
            self.percent = config.get('percent', None)
            self.amount = config.get('amount', None)
        else:
            self.percent = 1

        self.high = None

    def get_action(self, df):

        if self.high is None:
            if self.last_order is not None and self.last_order['action'] == SignalAction.BUY:
                self.high = max(df.close.max(), float(self.last_order['price']))
            else:
                return SignalAction.WAIT


        last_interval = df.tail(1)

        if last_interval.close.values[0] > self.high:
            self.high = last_interval.close.values[0]

        if self.percent is not None:
            threshold = self.high * (1 - (self.percent / 100))
        else:
            threshold = self.high - self.amount

        df.loc[df.index, 'trailing_stop_loss'] = threshold

        if last_interval.close.values[0] < threshold:
            return SignalAction.SELL

        return SignalAction.WAIT


    def render(self, df):
        filename = f'graphs/{self.alias}_trailing_stop_loss.png'

        self.log.debug(f'Trailing stop loss: Rendering chart {filename}')
        plt.close('all')
        plt.xticks(rotation=45)
        plt.plot(df.close, label='close')
        plt.plot(df.trailing_stop_loss, label='stop')
        plt.legend()
        plt.ylabel('Close')

        for action in self.action_list:
            plt.plot(action['time'], action['close'], 'g*' if action['action'] == SignalAction.BUY else 'r*', markersize=10, label='Buy' if action['action'] == SignalAction.BUY else 'Sell')

        plt.savefig(filename)

from traders.signals.signal_type import SignalAction
from traders.signals.signal import Signal
import matplotlib.pyplot as plt

MINIMUM_INTERVALS = 10

class MovingAverageSlope(Signal):
    def __init__(self, base_currency, log):
        super().__init__()
        self.log = log
        self.base_currency = base_currency


    def get_action(self, df):
        if df.shape[0] < 200:
            return SignalAction.WAIT

        if not 'sma50' in df.columns:
            df['sma50'] = df.close.rolling(25, min_periods=1).mean()
        if not 'sma200' in df.columns:
            df['sma200'] = df.close.rolling(200, min_periods=1).mean()

        if not 'diff_50' in df.columns:
            df['diff_50'] = df.sma50 - df.sma50.shift()

        latest_interval = df.tail(MINIMUM_INTERVALS)
        #self.log.debug(latest_interval)

        mas = []
        for i in range(0, MINIMUM_INTERVALS):
            mas.append(latest_interval.diff_50.values[i])

        action = SignalAction.WAIT

        if all(i > 0 for i in mas):
            self.log.debug(f'Last {MINIMUM_INTERVALS} intervals are increasing {mas}')
            action = SignalAction.BUY
        elif all(i < 0 for i in mas):
            self.log.debug(f'Last {MINIMUM_INTERVALS} intervals are decreasing {mas}')
            action = SignalAction.SELL

        if action != SignalAction.WAIT:
            self._add_action(action, latest_interval.index.values[0], latest_interval.close.values[0])

        self.render(df)

        return action


    def render(self, df):
        filename = f'graphs/{self.base_currency}_moving_average_slope.png'

        self.log.debug(f'Moving Average Slope Signal: Rendering chart {filename}')
        plt.close('all')
        plt.xticks(rotation=45)
        plt.plot(df.close, label='close')
        plt.plot(df.sma50, label='sma50')
        # plt.plot(df.sma200, label='sma200')
        plt.legend()
        plt.ylabel('Close')
        # for action in self.action_list:
        #     plt.plot(action['time'], action['close'], 'g*' if action['action'] == SignalAction.BUY else 'r*', markersize=10, label='Buy' if action['action'] == SignalAction.BUY else 'Sell')

        plt.savefig(filename)
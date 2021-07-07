from traders.signals.signal_action import SignalAction
from traders.signals.signal import Signal
import matplotlib.pyplot as plt


class ExponentialMovingAverageSlope(Signal):
    def __init__(self, log, alias, config=None):
        super().__init__()
        self.log = log
        self.alias = alias
        if config is not None:
            self.intervals = config['intervals']
            self.span = config['span']
        else:
            self.intervals = 10
            self.span = 8

    def get_action(self, df):
        if df.shape[0] < self.span:
            return SignalAction.WAIT

        if not 'ema' in df.columns:
            df['ema'] = df.close.ewm(span=self.span, adjust=False).mean()
        if not 'ema_diff' in df.columns:
            df['ema_diff'] = df.ema - df.ema.shift()

        action = SignalAction.WAIT

        latest_interval = df.tail(self.intervals)

        mas = []
        for i in range(0, self.intervals):
            mas.append(latest_interval.ema_diff.values[i])

        if all(i > 0 for i in mas):
            self.log.debug(f'{self.alias}: emas ^')
            action = SignalAction.BUY
        elif all(i < 0 for i in mas):
            self.log.debug(f'{self.alias}: emas v')
            action = SignalAction.SELL
        else:
            self.log.debug(f'{self.alias}: emas -')
        return action


    def calculate_percent_change_over_intervals(self, intervals, df):
        # lastest_intervals = df.tail(intervals + 1)
        # self.log.debug(lastest_intervals)

        last_row = df.shape[0] - 1
        start = df.close.values[last_row - intervals]
        end = df.close.values[last_row]
        return ((end - start)/start) * 100


    def render(self, df):
        filename = f'graphs/{self.alias}_exp_moving_average_slope.png'

        self.log.debug(f'Moving Average Slope Signal: Rendering chart {filename}')
        plt.close('all')
        plt.xticks(rotation=45)
        plt.plot(df.close, label='close')
        plt.plot(df.ema, label='ema')
        plt.legend()
        plt.ylabel('Close')
        plt.savefig(filename)
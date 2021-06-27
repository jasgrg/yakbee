from traders.signals.signal_type import SignalAction
from traders.signals.signal import Signal
import matplotlib.pyplot as plt

MINIMUM_INTERVALS = 10

class ExponentialMovingAverageSlope(Signal):
    def __init__(self, base_currency, log):
        super().__init__()
        self.log = log
        self.base_currency = base_currency


    def get_action(self, df):
        if df.shape[0] < 200:
            return SignalAction.WAIT

        if not 'ema' in df.columns:
            df['ema'] = df.close.ewm(span=8, adjust=False).mean()
        if not 'ema_diff' in df.columns:
            df['ema_diff'] = df.ema - df.ema.shift()

        latest_interval = df.tail(MINIMUM_INTERVALS)
        #self.log.debug(latest_interval)

        mas = []
        for i in range(0, MINIMUM_INTERVALS):
            mas.append(latest_interval.ema_diff.values[i])

        action = SignalAction.WAIT

        if all(i > 0 for i in mas):
            self.log.debug(f'Last {MINIMUM_INTERVALS} intervals are increasing {mas}')
            self.log.info(f'{self.base_currency} ^')
            action = SignalAction.BUY
        elif all(i < 0 for i in mas):
            self.log.debug(f'Last {MINIMUM_INTERVALS} intervals are decreasing {mas}')
            action = SignalAction.SELL
            self.log.info(f'{self.base_currency} v')
        else:
            self.log.info(f'{self.base_currency} -')

        if action != SignalAction.WAIT:
            self._add_action(action, latest_interval.index.values[0], latest_interval.close.values[0])

        self.render(df)

        return action


    def render(self, df):
        filename = f'graphs/{self.base_currency}_exp_moving_average_slope.png'

        self.log.debug(f'Moving Average Slope Signal: Rendering chart {filename}')
        plt.close('all')
        plt.xticks(rotation=45)
        plt.plot(df.close, label='close')
        plt.plot(df.ema, label='ema')
        plt.legend()
        plt.ylabel('Close')
        plt.savefig(filename)
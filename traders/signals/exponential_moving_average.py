from traders.signals.signal_action import SignalAction
from traders.signals.signal import Signal
import matplotlib.pyplot as plt

class ExponentialMovingAverage(Signal):
    def __init__(self, log, alias,  config=None):
        super().__init__()
        self.log = log
        self.alias = alias
        if config is not None:
            self.short = config['short']
            self.long = config['long']
        else:
            self.short = 12
            self.long = 26

        self.short_col = f'ema{self.short}'
        self.long_col = f'ema{self.long}'

        self.history = None


    def get_action(self, df):
        if df.shape[0] < self.long:
            return SignalAction.WAIT

        short_col = self.short_col
        long_col = self.long_col
        gt_col = f'{short_col}_gt_{long_col}'
        lt_col = f'{short_col}_lt_{long_col}'

        if not short_col in df.columns:
            df[short_col] = df.close.ewm(span=self.short, adjust=False).mean()
        if not long_col in df.columns:
            df[long_col] = df.close.ewm(span=self.long, adjust=False).mean()

        if not gt_col in df.columns:
            df[gt_col] = df[short_col] > df[long_col]

        if not lt_col in df.columns:
            df[lt_col] = df[short_col] < df[long_col]

        latest_interval = df.tail(1)

        action = SignalAction.WAIT

        if latest_interval[gt_col].values[0] == True:
            self.log.debug(f'{short_col} {latest_interval[short_col].values[0]} is over {long_col} {latest_interval[long_col].values[0]}')
            action = SignalAction.BUY
        elif latest_interval[lt_col].values[0] == True:
            self.log.debug(f'{short_col} {latest_interval[short_col].values[0]} is under {long_col} {latest_interval[long_col].values[0]}')
            action = SignalAction.SELL


        self._add_to_history(latest_interval)

        return action

    def render(self, df):
        df = self.history
        filename = f'graphs/{self.alias}_exponential_moving_average.png'

        self.log.debug(f'Exponential Moving Average Signal: Rendering chart {filename}')
        plt.close('all')
        plt.xticks(rotation=45)
        plt.plot(df.close, label="Close")
        plt.plot(df[self.short_col], label=self.short_col)
        plt.plot(df[self.long_col], label=self.long_col)
        plt.legend()
        plt.ylabel('Close')

        plt.savefig(filename)

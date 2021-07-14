from traders.signals.signal_action import SignalAction
from traders.signals.signal import Signal
import matplotlib.pyplot as plt


###
# Moving average covergence divergence
# https://www.investopedia.com/terms/m/macd.asp
###
import pandas as pd
class MACD(Signal):
    def __init__(self, log, alias, config=None):
        super().__init__()
        self.log = log
        self.alias = alias
        if config is not None:
            self.short = config['short']
            self.long = config['long']
            self.span = config['span']
        else:
            self.short = 12
            self.long = 26
            self.span = 9

        self.short_col = f'ema{self.short}'
        self.long_col = f'ema{self.long}'

    def get_action(self, df):
        if df.shape[0] < self.long:
            return SignalAction.WAIT

        short_col = self.short_col
        long_col = self.long_col

        if not short_col in df.columns:
            df[short_col] = df.close.ewm(span=self.short, adjust=False).mean()
        if not long_col in df.columns:
            df[long_col] = df.close.ewm(span=self.long, adjust=False).mean()

        if not 'macd' in df.columns:
            df['macd'] = df[short_col] - df[long_col]
        if not 'macd_signal' in df.columns:
            df['macd_signal'] = df.macd.ewm(span=self.span, adjust=False).mean()

        if not 'macd_gt_signal' in df.columns:
            df['macd_gt_signal'] = df.macd > df.macd_signal

        if not 'macd_lt_signal' in df.columns:
            df['macd_lt_signal'] = df.macd < df.macd_signal


        latest_interval = df.tail(1)

        action = SignalAction.WAIT
        if latest_interval['macd_gt_signal'].values[0] == True:
            action = SignalAction.BUY
        elif latest_interval['macd_lt_signal'].values[0] == True:
            action = SignalAction.SELL

        self._add_to_history(latest_interval)

        return action

    def render(self, df):
        df = self.history
        filename = f'graphs/{self.alias}_macd.png'

        self.log.debug(f'Exponential Moving Average Signal: Rendering chart {filename}')
        plt.close('all')
        plt.xticks(rotation=45)
        plt.plot(df.macd, label='macd')
        plt.plot(df.macd_signal, label='signal')
        plt.legend()
        plt.ylabel('Close')
        plt.savefig(filename)

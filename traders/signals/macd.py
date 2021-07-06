from traders.signals.signal_action import SignalAction
from traders.signals.signal import Signal
import matplotlib.pyplot as plt


###
# Moving average covergence divergence
# https://www.investopedia.com/terms/m/macd.asp
###
import pandas as pd
class MACD(Signal):
    def __init__(self, log, alias):
        super().__init__()
        self.log = log
        self.alias = alias

    def get_action(self, df):
        if not 'ema12' in df.columns:
            df['ema12'] = df.close.ewm(span=12, adjust=False).mean()
        if not 'ema26' in df.columns:
            df['ema26'] = df.close.ewm(span=26, adjust=False).mean()

        if not 'macd' in df.columns:
            df['macd'] = df.ema12 - df.ema26
        if not 'macd_signal' in df.columns:
            df['macd_signal'] = df.macd.ewm(span=9, adjust=False).mean()

        if not 'macd_gt_signal' in df.columns:
            df['macd_gt_signal'] = df.macd > df.macd_signal

        if not 'macd_lt_signal' in df.columns:
            df['macd_lt_signal'] = df.macd < df.macd_signal


        latest_interval = df.tail(1)

        action = SignalAction.WAIT
        if latest_interval['macd_gt_signal'].values[0] is True:
            action = SignalAction.BUY
        elif latest_interval['macd_lt_signal'].values[0] is True:
            action = SignalAction.SELL

        #self.render(df)

        return action



    def render(self, df):
        filename = f'graphs/{self.alias}_macd.png'

        self.log.debug(f'Exponential Moving Average Signal: Rendering chart {filename}')
        plt.close('all')
        plt.xticks(rotation=45)
        #plt.plot(df.close, label='close')
        plt.plot(df.macd, label='macd')
        plt.plot(df.macd_signal, label='signal')
        plt.legend()
        plt.ylabel('Close')
        plt.savefig(filename)
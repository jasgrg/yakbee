from traders.signals.signal_type import SignalAction
from traders.signals.signal import Signal
import matplotlib.pyplot as plt

class ExponentialMovingAverage(Signal):
    def __init__(self, log):
        super().__init__()
        self.log = log


    def get_action(self, df):
        if df.shape[0] < 26:
            return SignalAction.WAIT

        if not 'ema8' in df.columns:
            df['ema8'] = df.close.ewm(span=8, adjust=False).mean()
        if not 'ema12' in df.columns:
            df['ema12'] = df.close.ewm(span=12, adjust=False).mean()
        if not 'ema26' in df.columns:
            df['ema26'] = df.close.ewm(span=26, adjust=False).mean()

        if not 'ema8_gt_ema12' in df.columns:
            df['ema8_gt_ema12'] = df.ema8 > df.ema12

        if not 'ema8_lt_ema12' in df.columns:
            df['ema8_lt_ema12'] = df.ema8 < df.ema12

        if not 'ema12_gt_ema26' in df.columns:
            df['ema12_gt_ema26'] = df.ema12 > df.ema26

        if not 'ema12_lt_ema26' in df.columns:
            df['ema12_lt_ema26'] = df.ema12 < df.ema26


        latest_interval = df.tail(1)

        action = SignalAction.WAIT

        if latest_interval['ema12_gt_ema26'].values[0] == True:
            self.log.debug(f'ema12 {latest_interval.ema12.values[0]} is over ema26 {latest_interval.ema26.values[0]}')
            action = SignalAction.BUY
        elif latest_interval['ema12_lt_ema26'].values[0] == True:
            self.log.debug(f'eam12 {latest_interval.ema12.values[0]} is under ema26 {latest_interval.ema26.values[0]}')
            action = SignalAction.SELL

        if action != SignalAction.WAIT:
            self._add_action(action, latest_interval.index.values[0], latest_interval.close.values[0])
        return action


    def render(self, df):
        filename = 'graphs/exponential_moving_average.png'

        self.log.debug(f'Exponential Moving Average Signal: Rendering chart {filename}')
        plt.close('all')
        plt.xticks(rotation=45)
        plt.plot(df.close, label='close')
        plt.plot(df.ema8, label='ema8')
        plt.plot(df.ema12, label='ema12')
        plt.plot(df.ema26, label='ema26')
        plt.legend()
        plt.ylabel('Close')
        for action in self.action_list:
            plt.plot(action['time'], action['close'], 'g*' if action['action'] == SignalAction.BUY else 'r*', markersize=10, label='Buy' if action['action'] == SignalAction.BUY else 'Sell')

        plt.savefig(filename)
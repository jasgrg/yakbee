from traders.signals.signal_action import SignalAction
from traders.signals.signal import Signal
from numpy import maximum
import matplotlib.pyplot as plt


class ThreeBlackCrows(Signal):
    def __init__(self, log, alias):
        super().__init__()
        self.log = log
        self.alias = alias

    def get_action(self, df):
        if not 'three_black_crows' in df.columns:
            df['three_black_crows'] = ((df.open < df.open.shift(1)) & (df.open > df.close.shift(1))) \
                & (df.close < df.low.shift(1)) \
                & (df.low - maximum(df.open, df.close) < (abs(df.open - df.close))) \
                & ((df.open.shift(1) < df.open.shift(2)) & (df.open.shift(1) > df.close.shift(2))) \
                & (df.close.shift(1) < df.low.shift(2)) \
                & (df.low.shift(1) - maximum(df.open.shift(1), df.close.shift(1)) < (abs(df.open.shift(1) - df.close.shift(1))))

        latest_interval = df.tail(1)

        action = SignalAction.WAIT

        if latest_interval.three_black_crows.values[0]:
            self.log.debug(f'{self.alias}: Three black crows found at {latest_interval.index.values[0]}')
            action = SignalAction.SELL

        if action != SignalAction.WAIT:
            self._add_action(action, latest_interval.index.values[0], latest_interval.close.values[0])

        return action

    def render(self, df):
        filename = f'graphs/{self.alias}_three_black_crows.png'

        self.log.debug(f'Three black crows: Rendering chart {filename}')
        plt.close('all')
        plt.xticks(rotation=45)
        plt.plot(df.close, label='close')
        plt.legend()
        plt.ylabel('Close')

        for action in self.action_list:
            plt.plot(action['time'], action['close'], 'g*' if action['action'] == SignalAction.BUY else 'r*', markersize=10, label='Buy' if action['action'] == SignalAction.BUY else 'Sell')

        plt.savefig(filename)
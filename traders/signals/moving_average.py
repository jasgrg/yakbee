from traders.signals.signal_action import SignalAction
from traders.signals.signal import Signal
import matplotlib.pyplot as plt

class MovingAverage(Signal):
    def __init__(self, log, alias):
        super().__init__()
        self.log = log
        self.alias = alias


    def get_action(self, df):
        if df.shape[0] < 200:
            return SignalAction.WAIT

        if not 'sma50' in df.columns:
            df['sma50'] = df.close.rolling(50, min_periods=1).mean()
        if not 'sma200' in df.columns:
            df['sma200'] = df.close.rolling(200, min_periods=1).mean()

        if not 'sma50_gt_sma200' in df.columns:
            df['sma50_gt_sma200'] = df.sma50 > df.sma200

        if not 'sma50_lt_sma200' in df.columns:
            df['sma50_lt_sma200'] = df.sma50 < df.sma200

        latest_interval = df.tail(1)

        self.log.debug(f'Moving Average Signals: sma50 {latest_interval.sma50.values[0]} | sma200 {latest_interval.sma200.values[0]}')

        action = SignalAction.WAIT

        if latest_interval['sma50_gt_sma200'].values[0] == True:
            self.log.debug(f'sma50 {latest_interval["sma50"].values[0]} has crossed over sma200 {latest_interval["sma200"].values[0]}')
            action = SignalAction.BUY
        elif latest_interval['sma50_lt_sma200'].values[0] == True:
            self.log.debug(f'sma50 {latest_interval["sma50"].values[0]} has crossed under sma200 {latest_interval["sma200"].values[0]}')
            action = SignalAction.SELL

        if action != SignalAction.WAIT:
            self._add_action(action, latest_interval.index.values[0], latest_interval.close.values[0])

        return action


    def render(self, df):
        filename = f'graphs/{self.alias}_moving_average.png'

        self.log.debug(f'Moving Average Signal: Rendering chart {filename}')
        plt.close('all')
        plt.xticks(rotation=45)
        plt.plot(df.close, label='close')
        plt.plot(df.sma50, label='sma50')
        plt.plot(df.sma200, label='sma200')
        plt.legend()
        plt.ylabel('Close')
        for action in self.action_list:
            plt.plot(action['time'], action['close'], 'g*' if action['action'] == SignalAction.BUY else 'r*', markersize=10, label='Buy' if action['action'] == SignalAction.BUY else 'Sell')

        plt.savefig(filename)
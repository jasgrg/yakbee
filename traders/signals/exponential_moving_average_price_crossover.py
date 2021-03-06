from traders.signals.signal_action import SignalAction
from traders.signals.signal import Signal
import matplotlib.pyplot as plt

class ExponentialMovingAveragePriceCrossover(Signal):
    def __init__(self, log, alias, config=None):
        super().__init__()
        self.log = log
        self.alias = alias
        if config is not None:
            self.ema = config['ema']
        else:
            self.ema = 20

        self.ema_col = f'ema{self.ema}'

    def get_action(self, df):
        if df.shape[0] < self.ema:
            return SignalAction.WAIT

        ema_col = self.ema_col
        gt_col = f'close_gt_{ema_col}'
        lt_col = f'close_lt_{ema_col}'
        gt_co_col = f'{gt_col}_cross_over'
        lt_co_col = f'{lt_col}_cross_over'

        df[ema_col] = df.close.ewm(span=self.ema, min_periods=self.ema, adjust=False).mean()

        df[gt_col] = df.close > df[ema_col]
        df[gt_co_col] = df[gt_col].ne(df[gt_col].shift())
        df.loc[df[gt_col] == False, gt_co_col] = False

        df[lt_col] = df.close < df[ema_col]
        df[lt_co_col] = df[lt_col].ne(df[lt_col].shift())
        df.loc[df[lt_col] == False, lt_co_col] = False

        df[gt_co_col] = df[gt_col].ne(df[gt_col].shift())
        df.loc[df[gt_col] == False, gt_co_col] = False

        df[lt_co_col] = df[lt_col].ne(df[lt_col].shift())
        df.loc[df[lt_col] == False, lt_co_col] = False

        latest_interval = df.tail(1)

        self.log.debug(f'Exponential Moving Average Signal: Price {latest_interval.close.values[0]} | {ema_col} {latest_interval[ema_col].values[0]} at {latest_interval.index.values[0]} | {latest_interval.close.values[0]}')

        action = SignalAction.WAIT

        if latest_interval[gt_co_col].values[0] == True:
            self.log.debug(f'Price {latest_interval.close.values[0]} has crossed over {ema_col} {latest_interval[ema_col].values[0]} at {latest_interval.index.values[0]}')
            action = SignalAction.BUY
        elif latest_interval[lt_co_col].values[0] == True:
            self.log.debug(f'Price {latest_interval.close.values[0]} has crossed under {ema_col} {latest_interval[ema_col].values[0]} at {latest_interval.index.values[0]}')
            action = SignalAction.SELL

        if action != SignalAction.WAIT:
            self._add_action(action, latest_interval.index.values[0], latest_interval.close.values[0])

        self._add_to_history(latest_interval)

        return action

    def render(self, df):
        df = self.history
        if self.history is None:
            return
        filename = f'graphs/{self.alias}_exponential_moving_average_crossover.png'

        self.log.debug(f'Exponential Moving Average Signal: Rendering chart {filename}')
        plt.close('all')
        plt.xticks(rotation=45)
        plt.plot(df.close, label='close')
        plt.plot(df[self.ema_col], label=self.ema_col)
        plt.legend()
        plt.ylabel('Close')

        min_date = df.epoch.values[0]

        actions = [o for o in self.action_list if o['epoch'] > min_date]

        for action in actions:
            plt.plot(action['time'], action['close'], 'g*' if action['action'] == SignalAction.BUY else 'r*', markersize=10, label='Buy' if action['action'] == SignalAction.BUY else 'Sell')
        plt.savefig(filename)

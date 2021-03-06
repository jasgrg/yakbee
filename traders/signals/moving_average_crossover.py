from traders.signals.signal_action import SignalAction
from traders.signals.signal import Signal
import matplotlib.pyplot as plt

class MovingAverageCrossover(Signal):
    def __init__(self, log, alias, config=None):
        super().__init__()
        self.log = log
        self.alias = alias
        if config is not None:
            self.short = config['short']
            self.long = config['long']
        else:
            self.short = 50
            self.long = 200

        self.short_col = f'sma{self.short}'
        self.long_col = f'sma{self.long}'

    def get_action(self, df):
        if df.shape[0] < self.long:
            return SignalAction.WAIT

        short_col = self.short_col
        long_col = self.long_col
        gt_col = f'{short_col}_gt_{long_col}'
        lt_col = f'{short_col}_lt_{long_col}'
        gt_co_col = f'{gt_col}_cross_over'
        lt_co_col = f'{lt_col}_cross_over'


        if not short_col in df.columns:
            df[short_col] = df.close.rolling(self.short, min_periods=1).mean()
        if not long_col in df.columns:
            df[long_col] = df.close.rolling(self.long, min_periods=1).mean()

        if not gt_col in df.columns:
            df[gt_col] = df[short_col] > df[long_col]
        if not gt_co_col in df.columns:
            df[gt_co_col] = df[gt_col].ne(df[gt_col].shift())
            df.loc[df[gt_col] == False, gt_co_col] = False

        if not lt_col in df.columns:
            df[lt_col] = df[short_col] < df[long_col]
        if not lt_co_col in df.columns:
            df[lt_co_col] = df[lt_col].ne(df[lt_col].shift())
            df.loc[df[lt_col] == False, lt_co_col] = False

        if not gt_co_col in df.columns:
            df[gt_co_col] = df[gt_col].ne(df[gt_col].shift())
        df.loc[df[gt_col] == False, gt_co_col] = False

        if not lt_co_col in df.columns:
            df[lt_co_col] = df[lt_col].ne(df[lt_col].shift())
        df.loc[df[lt_col] == False, lt_co_col] = False

        latest_interval = df.tail(1)

        self.log.debug(f'Moving Average Signals: short {latest_interval[short_col].values[0]} | long {latest_interval[long_col].values[0]}')

        action = SignalAction.WAIT

        if latest_interval[gt_co_col].values[0] == True:
            self.log.debug(f'{short_col} {latest_interval[short_col].values[0]} has crossed over {long_col} {latest_interval[long_col].values[0]}')
            action = SignalAction.BUY
        elif latest_interval[lt_co_col].values[0] == True:
            self.log.debug(f'{short_col} {latest_interval[short_col].values[0]} has crossed under {long_col} {latest_interval[long_col].values[0]}')
            action = SignalAction.SELL

        if action != SignalAction.WAIT:
            self._add_action(action, latest_interval.index.values[0], latest_interval.close.values[0])

        self._add_to_history(latest_interval)

        return action


    def render(self, df):
        df = self.history
        filename = f'graphs/{self.alias}_moving_average_crossover.png'

        self.log.debug(f'Moving Average Signal: Rendering chart {filename}')
        plt.close('all')
        plt.xticks(rotation=45)
        plt.plot(df.close, label='close')
        plt.plot(df[self.short_col], label=self.short_col)
        plt.plot(df[self.long_col], label=self.long_col)
        plt.legend()
        plt.ylabel('Close')

        for action in self.action_list:
            plt.plot(action['time'], action['close'], 'g*' if action['action'] == SignalAction.BUY else 'r*', markersize=10, label='Buy' if action['action'] == SignalAction.BUY else 'Sell')

        plt.savefig(filename)
from traders.signals.signal_action import SignalAction
from traders.signals.signal import Signal
import matplotlib.pyplot as plt

class MovingAveragePriceCrossover(Signal):
    def __init__(self, log, alias, config=None):
        super().__init__()
        self.log = log
        self.alias = alias
        if config is not None:
            self.sma = config['sma']
        else:
            self.sma = 100

        self.sma_col = f'sma{self.sma}'

    def get_action(self, df):
        if df.shape[0] < self.sma:
            return SignalAction.WAIT

        sma_col = self.sma_col
        gt_col = f'close_gt_{sma_col}'
        lt_col = f'close_lt_{sma_col}'
        gt_co_col = f'{gt_col}_cross_over'
        lt_co_col = f'{lt_col}_cross_over'


        if not sma_col in df.columns:
            df[sma_col] = df.close.rolling(self.sma, min_periods=1).mean()

        if not gt_col in df.columns:
            df[gt_col] = df.close > df[sma_col]
        if not gt_co_col in df.columns:
            df[gt_co_col] = df[gt_col].ne(df[gt_col].shift())
            df.loc[df[gt_col] == False, gt_co_col] = False

        if not lt_col in df.columns:
            df[lt_col] = df.close < df[sma_col]
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

        self.log.info(f'Moving Average Signals: Price {latest_interval.close.values[0]} | long {latest_interval[sma_col].values[0]}')

        action = SignalAction.WAIT

        if latest_interval[gt_co_col].values[0] == True:
            self.log.debug(f'Price {latest_interval.close.values[0]} has crossed over {sma_col} {latest_interval[sma_col].values[0]}')
            action = SignalAction.BUY
        elif latest_interval[lt_co_col].values[0] == True:
            self.log.debug(f'Price {latest_interval.close.values[0]} has crossed under {sma_col} {latest_interval[sma_col].values[0]}')
            action = SignalAction.SELL

        if action != SignalAction.WAIT:
            self._add_action(action, latest_interval.index.values[0], latest_interval.close.values[0])
        #self.render(df)
        return action


    def render(self, df):
        filename = f'graphs/{self.alias}_moving_average_price_crossover.png'

        self.log.debug(f'Moving Average Signal: Rendering chart {filename}')
        plt.close('all')
        plt.xticks(rotation=45)
        plt.plot(df.close, label='close')
        plt.plot(df[self.sma_col], label=self.sma_col)
        plt.legend()
        plt.ylabel('Close')

        # for action in self.action_list:
        #     plt.plot(action['time'], action['close'], 'g*' if action['action'] == SignalAction.BUY else 'r*', smarkersize=10, label='Buy' if action['action'] == SignalAction.BUY else 'Sell')

        plt.savefig(filename)
from traders.signals.signal_action import SignalAction
from traders.signals.signal import Signal
import matplotlib.pyplot as plt

MINIMUM_INTERVALS = 10
EMA_SPAN = 8

INTERVAL_SLOPES = [
    # {
    #     'intervals': 8,
    #     'min_change_percent': 1
    # },
    # {
    #     'intervals': 3,
    #     'min_change_percent': 2.2
    # }
]



class ExponentialMovingAverageSlope(Signal):
    def __init__(self, log, alias):
        super().__init__()
        self.log = log
        self.alias = alias


    def get_action(self, df):
        if df.shape[0] < EMA_SPAN:
            return SignalAction.WAIT

        if not 'ema' in df.columns:
            df['ema'] = df.close.ewm(span=EMA_SPAN, adjust=False).mean()
        if not 'ema_diff' in df.columns:
            df['ema_diff'] = df.ema - df.ema.shift()

        action = SignalAction.WAIT

        for i_slope in INTERVAL_SLOPES:
            percent_change = self.calculate_percent_change_over_intervals(i_slope['intervals'], df)
            self.log.debug(f'Slope over last {i_slope["intervals"]} at {df.index.values[df.shape[0]-1]} intervals is {percent_change}')
            if percent_change > i_slope['min_change_percent']:
                self.log.debug(f'Slope over last {i_slope["intervals"]} intervals is {percent_change} which is greater than {i_slope["min_change_percent"]}')
                return SignalAction.BUY
            elif percent_change * -1 > i_slope['min_change_percent']:
                self.log.debug(f'Slope over last {i_slope["intervals"]} intervals is {percent_change} which is less than {i_slope["min_change_percent"]}')
                return SignalAction.SELL


        latest_interval = df.tail(MINIMUM_INTERVALS)

        mas = []
        for i in range(0, MINIMUM_INTERVALS):
            mas.append(latest_interval.ema_diff.values[i])

        if all(i > 0 for i in mas):
            self.log.debug(f'{self.alias}: emas ^')
            action = SignalAction.BUY
        elif all(i < 0 for i in mas):
            self.log.debug(f'{self.alias}: emas v')
            action = SignalAction.SELL
        else:
            self.log.debug(f'{self.alias}: emas -')
        return action


    def calculate_percent_change_over_intervals(self, intervals, df):
        # lastest_intervals = df.tail(intervals + 1)
        # self.log.debug(lastest_intervals)

        last_row = df.shape[0] - 1
        start = df.close.values[last_row - intervals]
        end = df.close.values[last_row]
        return ((end - start)/start) * 100


    def render(self, df):
        filename = f'graphs/{self.alias}_exp_moving_average_slope.png'

        self.log.debug(f'Moving Average Slope Signal: Rendering chart {filename}')
        plt.close('all')
        plt.xticks(rotation=45)
        plt.plot(df.close, label='close')
        plt.plot(df.ema, label='ema')
        plt.legend()
        plt.ylabel('Close')
        plt.savefig(filename)
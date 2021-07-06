from traders.signals.signal_action import SignalAction
from traders.signals.signal import Signal
import matplotlib.pyplot as plt


class ElderRay(Signal):
    def __init__(self, log, alias,  config=None):
        super().__init__()
        self.log = log
        self.alias = alias
        if config is not None:
            self.span = config['span']
        else:
            self.span = 13
        self.col = f'ema{self.span}'



    def get_action(self, df):
        if not self.col in df.columns:
            df[self.col] = df.close.ewm(span=self.span, adjust=False).mean()

        df['elder_ray_bull'] = df['high'] - df[self.col]
        df['elder_ray_bear'] = df['low'] - df[self.col]

        df['eri_buy'] = ((df['elder_ray_bear'] < 0) & (
                    df['elder_ray_bear'] > df['elder_ray_bear'].shift(1))) | (
                             (df['elder_ray_bull'] > df['elder_ray_bull'].shift(1)))

        df['eri_sell'] = ((df['elder_ray_bull'] > 0) & (
                    df['elder_ray_bull'] < df['elder_ray_bull'].shift(1))) | (
                              (df['elder_ray_bear'] < df['elder_ray_bear'].shift(1)))

        latest_interval = df.tail(1)

        action = SignalAction.WAIT

        if latest_interval['eri_buy'].values[0]:
            action = SignalAction.BUY
        elif latest_interval['eri_sell'].values[0]:
            action = SignalAction.SELL

        return action


    def render(self, df):
        filename = f'graphs/{self.alias}_elder_ray.png'

        self.log.debug(f'Elder Ray Signal: Rendering chart {filename}')
        plt.close('all')
        plt.xticks(rotation=45)
        plt.plot(df['elder_ray_bull'], label='bull power')
        plt.plot(df['elder_ray_bear'], label='bear power')
        plt.legend()
        plt.ylabel('Close')

        plt.savefig(filename)

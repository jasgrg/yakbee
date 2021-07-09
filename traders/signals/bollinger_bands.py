from traders.signals.signal_action import SignalAction
from traders.signals.signal import Signal
import matplotlib.pyplot as plt


class BollingerBands(Signal):
    def __init__(self, log, alias,  config=None):
        super().__init__()
        self.log = log
        self.alias = alias

        if config is not None:
            self.span = config['span']
        else:
            self.span = 20

    def get_action(self, df):
        df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
        df['std'] = df['typical_price'].rolling(self.span).std(ddof=0)
        df['MATP'] = df['typical_price'].rolling(self.span).mean()

        df['BOLU'] = df['MATP'] + 2 * df['std']
        df['BOLD'] = df['MATP'] - 2 * df['std']

        return SignalAction.WAIT


    def render(self, df):
        filename = f'graphs/{self.alias}_bollinger_bands.png'

        self.log.debug(f'Bollinger Bands: Rendering chart {filename}')
        plt.close('all')
        plt.xticks(rotation=45)
        plt.plot(df['BOLU'], label='Upper Bolling Band')
        plt.plot(df['typical_price'], label='Typical Price')
        plt.plot(df['BOLD'], label='Lower Bolling Band')
        plt.legend()
        plt.ylabel('Close')

        plt.savefig(filename)

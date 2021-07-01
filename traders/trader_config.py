from traders.signals.moving_average import MovingAverage
from traders.signals.moving_average_crossover import MovingAverageCrossover
from traders.signals.exponential_moving_average import ExponentialMovingAverage
from traders.signals.exponential_moving_average_crossover import ExponentialMovingAverageCrossover
from traders.signals.macd import MACD
from traders.signals.moving_average_slope import MovingAverageSlope
from traders.signals.exponential_moving_average_slope import ExponentialMovingAverageSlope
from traders.signals.three_black_crows import ThreeBlackCrows
from traders.signals.three_white_soldiers import ThreeWhiteSoldiers

from traders.strategy import Strategy

signal_defs = {
    'moving_average': MovingAverage,
    'moving_average_slope': MovingAverageSlope,
    'moving_average_crossover': MovingAverageCrossover,
    'exponential_moving_average': ExponentialMovingAverage,
    'exponential_moving_average_crossover': ExponentialMovingAverageCrossover,
    'exponential_moving_average_slope': ExponentialMovingAverageSlope,
    'macd': MACD,
    'three_black_crows': ThreeBlackCrows,
    'three_white_soldiers': ThreeWhiteSoldiers
}


class TraderConfig:
    def __init__(self, config, log):
        self.name = config['name']
        self.base_currency = config['config']['base_currency']
        self.quote_currency = config['config']['quote_currency']
        self.granularity = config['config']['granularity']
        self.sell_at_loss = config['config'].get('sell_at_loss', 'True') == 'True'
        self.min_gain_to_sell = config['config'].get('min_gain_to_sell', 0)
        self.alias = config.get('alias', self.base_currency)
        self.live = config['live']
        self.buy_strategies = self.get_strategies(config['config']['buy_strategies'], log)
        self.sell_strategies = self.get_strategies(config['config']['sell_strategies'], log)
        self.auth = config['auth']

    def get_strategies(self, strategies, log):
        strats = []
        for strategy in strategies:
            signals = []
            for sig in strategy:
                signals.append(signal_defs[sig](log, self.alias))
            strats.append(Strategy(signals))
        return strats

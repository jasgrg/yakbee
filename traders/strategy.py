from traders.signals.signal_action import SignalAction
from traders.signals.moving_average import MovingAverage
from traders.signals.moving_average_crossover import MovingAverageCrossover
from traders.signals.exponential_moving_average import ExponentialMovingAverage
from traders.signals.exponential_moving_average_crossover import ExponentialMovingAverageCrossover
from traders.signals.macd import MACD
from traders.signals.moving_average_slope import MovingAverageSlope
from traders.signals.exponential_moving_average_slope import ExponentialMovingAverageSlope
from traders.signals.three_black_crows import ThreeBlackCrows
from traders.signals.three_white_soldiers import ThreeWhiteSoldiers
from traders.signals.macd_crossover import MACDCrossover
from traders.signals.elder_ray import ElderRay
from traders.signals.trailing_stop_loss import TrailingStopLoss
from traders.signals.bollinger_bands import BollingerBands
from traders.signals.exponential_moving_average_price_crossover import ExponentialMovingAveragePriceCrossover
from traders.signals.moving_average_price_crossover import MovingAveragePriceCrossover

signal_defs = {
    'moving_average': MovingAverage,
    'moving_average_slope': MovingAverageSlope,
    'moving_average_crossover': MovingAverageCrossover,
    'moving_average_price_crossover': MovingAveragePriceCrossover,
    'exponential_moving_average': ExponentialMovingAverage,
    'exponential_moving_average_crossover': ExponentialMovingAverageCrossover,
    'exponential_moving_average_slope': ExponentialMovingAverageSlope,
    'exponential_moving_average_price_crossover': ExponentialMovingAveragePriceCrossover,
    'macd': MACD,
    'three_black_crows': ThreeBlackCrows,
    'three_white_soldiers': ThreeWhiteSoldiers,
    'macd_crossover': MACDCrossover,
    'golden_cross': MovingAverage,
    'elder_ray': ElderRay,
    'trailing_stop_loss': TrailingStopLoss,
    'bollinger_bands': BollingerBands,


}


class Strategy():
    def __init__(self, strategy, alias, log):
        if not isinstance(strategy, dict):
            self.signals = get_signals(strategy, alias, log)
            self.name = 'Unnamed'
            self.sell_at_loss = None
        else:
            self.signals = get_signals(strategy['signals'], alias, log)
            self.name = strategy['strategy']
            sell_at_loss = strategy.get('sell_at_loss', None)
            self.sell_at_loss = None if sell_at_loss is None else sell_at_loss == 1

        self.historical_data = None

    def get_action(self, historical_data, last_order):
        self.historical_data = historical_data

        action = SignalAction.WAIT

        votes = []

        for s in self.signals:
            s.set_last_order(last_order)
            votes.append(s.get_action(historical_data))

        # all signals must agree to initiate a trade
        if all(vote == SignalAction.BUY for vote in votes):
            action = SignalAction.BUY
        elif all(vote == SignalAction.SELL for vote in votes):
            action = SignalAction.SELL

        return action

    def render(self):
        if self.historical_data is None:
            return
        for s in self.signals:
            s.render(self.historical_data)


def get_signals(signals, alias, log):
    sigs = []
    for signal in signals:
        if isinstance(signal, str):
            sigs.append(signal_defs[signal](log, alias))
        else:
            sigs.append(signal_defs[signal['signal']](log, alias, signal))
    return sigs

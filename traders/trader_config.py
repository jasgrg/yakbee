from traders.strategy import Strategy, get_signals


class TraderConfig:
    def __init__(self, config, log):
        self.name = config['name']
        self.base_currency = config['config']['base_currency']
        self.quote_currency = config['config']['quote_currency']
        self.granularity = config['config']['granularity']
        self.sell_at_loss = config['config'].get('sell_at_loss', 0) == 1
        self.buy_near_high = config['config'].get('buy_near_high', 0) == 1
        self.min_gain_to_sell = config['config'].get('min_gain_to_sell', 0)
        self.alias = config.get('alias', self.base_currency)
        self.live = config['live']
        self.buy_strategies = self.get_strategies(config['config']['buy_strategies'], log)
        self.sell_strategies = self.get_strategies(config['config']['sell_strategies'], log)
        self.non_trading_signals = get_signals(config['config'].get('non_trading_signals', []), self.alias, log)
        self.auth = config['auth']

    def get_strategies(self, strategies, log):
        strats = []
        for strategy in strategies:
            strats.append(Strategy(strategy, self.alias, log))
        return strats



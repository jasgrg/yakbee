from models.config import Config
from log.logservice import Log
from sim.sim_trade_manager import SimTradeManager

def main():
    config = Config()
    log = Log(config)

    sim = SimTradeManager(config, log)

    traders = sim.create_traders(config.config)

    for trader in traders:
        for strategy in trader.config.buy_strategies:
            strategy.get_action(trader.historical_data, None)
            strategy.render()


if __name__ == '__main__':
    main()
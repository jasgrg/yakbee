from models.config import Config
from log.logservice import Log
from sim.sim_trade_manager import SimTradeManager

def main():
    config = Config()
    log = Log(config)

    sim = SimTradeManager(config, log)

    traders = sim.create_traders(config.config)

    for trader in traders:
        trader.historical_data.to_csv(f'datasets/{trader.config.alias}_{trader.config.granularity}.csv')


if __name__ == '__main__':
    main()
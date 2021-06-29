import time
from datetime import datetime, timedelta
import sched
from models.config import Config
from sim.sim_trader import SimTrader
from traders.trade_manager import TradeManager

SIM_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

class SimTradeManager(TradeManager):
    def __init__(self, config: Config, log):
        super().__init__(config, log)

        self.start_date = datetime.strptime(config.config['sim']['sim_start_date'], SIM_DATE_FORMAT)
        self.end_date = datetime.strptime(config.config['sim']['sim_end_date'], SIM_DATE_FORMAT)
        self.log = log

    def run(self):
        self.traders = self.create_traders(self.config.config)
        cur_date_time = self.start_date
        for trader in self.traders:
            while cur_date_time <= self.end_date:
                trader.calculate_and_trade(cur_date_time.timestamp())
                cur_date_time = cur_date_time + timedelta(seconds=trader.config.granularity)
            for trade in trader.trades:
                self.log.debug(f"{trader.config.name} | {trade['date']} | {trade['action']} | {trade['base_amt']} | {trade['quote_amt']} ")
            trader.render_strategies()

    def create_traders(self, config: Config) -> []:
        traders = []
        for t in config['traders']:
            traders.append(SimTrader(t, self.log, self.start_date, self.end_date))

        return traders

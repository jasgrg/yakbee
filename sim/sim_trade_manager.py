from datetime import datetime, timedelta
from models.config import Config
from sim.sim_trader import SimTrader
from traders.trade_manager import TradeManager

SIM_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


class SimTradeManager(TradeManager):
    def __init__(self, config: Config, log):
        super().__init__(config, log, None)

        self.start_date = datetime.strptime(config.config['sim']['sim_start_date'], SIM_DATE_FORMAT)
        self.end_date = datetime.strptime(config.config['sim']['sim_end_date'], SIM_DATE_FORMAT)
        self.log = log
        self.traders = []

    def run(self):
        self.traders = self.create_traders(self.config.config)
        cur_date_time = self.start_date

        for trader in self.traders:
            while cur_date_time <= self.end_date:
                trader.calculate_and_trade(cur_date_time.timestamp())
                cur_date_time = cur_date_time + timedelta(seconds=trader.config.granularity)
            cur_date_time = self.start_date

        for trader in self.traders:
            for trade in trader.exchange.get_filled_orders():
                self.log.debug(f"{trader.config.name} | {trade['date']} | {trade['action']} | {trade['size']} | {trade['price']} | {trade['size'] * trade['price']} ")
            self.log.debug(f'{trader.config.name} | {trader.exchange.get_available_amount(trader.config.base_currency)} {trader.config.base_currency}')
            self.log.debug(f'{trader.config.name} | {trader.exchange.get_available_amount(trader.config.quote_currency)} {trader.config.quote_currency}')
            trader.render_strategies()
            trader.render()

    def create_traders(self, config: Config) -> []:
        traders = []
        for t in config['traders']:
            traders.append(SimTrader(t, self.log, self.start_date, self.end_date))

        return traders

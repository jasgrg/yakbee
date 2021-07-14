from datetime import datetime, timedelta, timezone
from models.config import Config
from sim.sim_trader import SimTrader
from traders.trade_manager import TradeManager

SIM_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


class SimTradeManager(TradeManager):
    def __init__(self, config: Config, log):
        super().__init__(config, log, None)

        self.start_date = datetime.strptime(config.config['sim']['sim_start_date'], SIM_DATE_FORMAT).astimezone(timezone.utc)
        self.end_date = datetime.strptime(config.config['sim']['sim_end_date'], SIM_DATE_FORMAT).astimezone(timezone.utc)
        self.data_file = config.config['sim'].get('data_file', None)
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
            orders = [o for o in trader.exchange.get_filled_orders() if o['date'] > self.start_date]
            orders.reverse()
            for trade in orders:
                self.log.info(f"{trader.config.name} | {trade['date']} | {' * ' if trade.get('sim', False) else '   '} | {trade['action']} | {trade['size']} | {trade['price']} | {trade['size'] * trade['price']} | fee: {trade['fee']} ")
            base_amt = trader.exchange.get_available_amount(trader.config.base_currency)
            quote_amt = trader.exchange.get_available_amount(trader.config.quote_currency)
            self.log.info(f'{trader.config.name} finished with {base_amt} {trader.config.base_currency} | {quote_amt} {trader.config.quote_currency}')
            trader.render(trader.historical_data)

    def create_traders(self, config: Config) -> []:
        traders = []
        for t in config['traders']:
            traders.append(SimTrader(t, self.log, self.start_date, self.end_date, self.data_file))

        return traders

from datetime import datetime, timezone
from traders.signals.signal_action import SignalAction
import pandas as pd

class DummyExchange():
    def __init__(self, base_exchange, config, log, start_date = None, data_file=None):
        self.base_exchange = base_exchange
        self.log = log
        self.config = config


        self.orders = self.base_exchange.get_filled_orders()
        if start_date is not None:
            self.orders = [o for o in self.orders if o['date'] < start_date]

        if len(self.orders) > 0:
            last_order = self.orders[0]
            if last_order['action'] == SignalAction.BUY:
                self.amounts = {
                    self.config.base_currency: last_order['size'],
                    self.config.quote_currency: 0
                }
            else:
                self.amounts = {
                    self.config.base_currency: 0,
                    self.config.quote_currency: last_order['size'] * last_order['price']
                }
        else:
            self.amounts = {
                self.config.base_currency: self.base_exchange.get_available_amount(self.config.base_currency),
                self.config.quote_currency: self.base_exchange.get_available_amount(self.config.quote_currency)
            }

        if self.amounts[self.config.quote_currency] == 0 and self.amounts[self.config.base_currency] == 0:
            self.amounts[self.config.quote_currency] = 100


        self.log.info(f'Starting simulation with {self.amounts[self.config.base_currency]} {self.config.base_currency} | {self.amounts[self.config.quote_currency]} {self.config.quote_currency}')
        self.data_file = data_file

    def get_historic_data(self, granularity, start_date: datetime = None, end_date: datetime = None):
        if self.data_file is not None:
            df = pd.read_csv(self.data_file)
            df.set_index('date', inplace=True)
            return df
        else:
            return self.base_exchange.get_historic_data(granularity, start_date, end_date)

    def get_ticker(self):
        return self.base_exchange.get_ticker()

    def get_available_amount(self, currency) -> float:
        return self.amounts[currency]

    def market_buy(self, quote_quantity: float, close: float):
        fee = .005
        quote_minus_fees = quote_quantity * (1 - fee)
        to_buy = quote_minus_fees / close
        self.log.debug(f'Dummy exchange: Buying {to_buy} {self.config.base_currency} for {quote_minus_fees}')
        self.amounts[self.config.base_currency] = self.amounts[self.config.base_currency] + to_buy
        self.amounts[self.config.quote_currency] = self.amounts[self.config.quote_currency] - quote_quantity
        self.orders.insert(0, {
            'size': to_buy,
            'price': close,
            'action': SignalAction.BUY,
            'fee': quote_quantity * fee
        })

    def market_sell(self, base_quantity: float, close: float):
        fee = .005
        value_sold = base_quantity * close
        valus_after_fees = value_sold * (1 - fee)
        self.log.debug(f'Dummy exchange: Selling {valus_after_fees} {self.config.quote_currency}')

        self.amounts[self.config.quote_currency] = self.amounts[self.config.quote_currency] + valus_after_fees
        self.amounts[self.config.base_currency] = self.amounts[self.config.base_currency] - base_quantity

        self.orders.insert(0, {
            'size': base_quantity,
            'price': close,
            'action': SignalAction.SELL,
            'fee': value_sold * fee,
            'date': datetime.utcnow().astimezone(timezone.utc)
        })

    def get_last_action(self):
        return self.orders[0]['action'] if len(self.orders) > 0 else SignalAction.WAIT

    def get_last_order(self):
        return None if len(self.orders) == 0 else self.orders[0]

    def get_last_buy_order(self):
        return self.orders[0] if len(self.orders) > 0 \
                                 and self.orders[0]['action'] == SignalAction.BUY \
                else None

    def get_filled_orders(self):
        return self.orders

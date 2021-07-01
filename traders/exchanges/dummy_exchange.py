from datetime import datetime
from traders.signals.signal_action import SignalAction


class DummyExchange():
    def __init__(self, base_exchange, config, log):
        self.base_exchange = base_exchange
        self.log = log
        self.config = config
        self.amounts = {
            self.config.base_currency: self.base_exchange.get_available_amount(self.config.base_currency),
            self.config.quote_currency: self.base_exchange.get_available_amount(self.config.quote_currency)
        }
        self.orders = []

    def get_historic_data(self, granularity, start_date: datetime = None, end_date: datetime = None):
        return self.base_exchange.get_historic_data(granularity, start_date, end_date)
        # dataframe = pd.read_csv('datasets/ds1.csv')
        # return dataframe

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
        self.orders.append({
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

        self.orders.append({
            'size': base_quantity,
            'price': close,
            'action': SignalAction.SELL,
            'fee': value_sold * fee
        })

    def get_last_action(self):
        if len(self.orders) == 0:
            return self.base_exchange.get_last_action()
        else:
            return self.orders[len(self.orders - 1)]['action']

    def get_last_buy_order(self):
        if len(self.orders) == 0:
            return self.base_exchange.get_last_buy_order()
        else:
            return self.orders[len(self.orders) - 1] if self.orders[len(self.orders) - 1]['action'] == SignalAction.BUY else None

    def get_filled_orders(self):
        return self.orders

from traders.trader_config import TraderConfig
from traders.exchanges.coinbase_pro_exchange import CoinBaseProExchange
from traders.signals.signal_type import SignalAction
from traders.exchanges.dummy_exchange import DummyExchange
import matplotlib.pyplot as plt

class Trader():
    def __init__(self, config, log):
        self.log = log
        self.config = TraderConfig(config, log)
        self.market = f'{self.config.base_currency}-{self.config.quote_currency}'
        self.exchange = self.get_exchange(config['exchange'])
        self.last_calc_date = 0
        self.last_action = self.exchange.get_last_action()
        self.trades_to_render = []

    def calculate_and_trade(self, current_time):
        time_since_last_calc = current_time - self.last_calc_date
        if time_since_last_calc >= self.config.granularity:
            self.log.debug(f'{self.config.name} running calculations')
            self.last_calc_date = current_time
            historical_data = self.get_historical_data(current_time)

            if historical_data.shape[0] > 1:
                close = historical_data.tail(1).close.values[0]

                for strategy in self.config.buy_strategies:
                    action = strategy.get_action(historical_data, close)
                    if action == SignalAction.BUY and self.last_action != SignalAction.BUY:
                        self.log.debug('*** Strategy returned BUY ***')
                        self.last_action = SignalAction.BUY
                        if self.trade(SignalAction.BUY, close):
                            self.log.debug('*** Trade was successful ***')
                            self.log.critical(f'{self.config.name} bought at {historical_data.tail(1).close.values[0]}')
                            self.trades_to_render.append({'action': action, 'time': historical_data.tail(1).index.values[0], 'close': historical_data.tail(1).close.values[0]})
                            self.render(historical_data)
                        break

                for strategy in self.config.sell_strategies:
                    action = strategy.get_action(historical_data, close)
                    if action == SignalAction.SELL and self.last_action != SignalAction.SELL:
                        self.log.debug('*** Strategy returned SELLs ***')
                        last_buy_order = self.exchange.get_last_buy_order()
                        if self.config.sell_at_loss or last_buy_order is None or float(last_buy_order['price']) < close:
                            self.last_action = SignalAction.SELL
                            if self.trade(SignalAction.SELL, close):
                                self.log.debug('*** Trade was successful ***')
                                self.log.critical(f'{self.config.name} sold at {historical_data.tail(1).close.values[0]}')
                                self.trades_to_render.append(
                                    {'action': action, 'time': historical_data.tail(1).index.values[0],
                                     'close': historical_data.tail(1).close.values[0]})
                                self.render(historical_data)
                            break
                        else:
                            self.log.debug(f'Cannot sell at a loss : current price {close} : purchased price {last_buy_order["price"]}')


    def get_historical_data(self, current_time):
        return self.exchange.get_historic_data(self.config.granularity)


    def trade(self, action:SignalAction, close: float):

        #TODO: set buy/sell limits, percentages, etc.
        base_currency_amount = self.exchange.get_available_amount(self.config.base_currency)
        quote_currency_amount = self.exchange.get_available_amount(self.config.quote_currency)

        if action == SignalAction.BUY and quote_currency_amount == 0:
            self.log.debug(f'Action is buy but balance is 0 {self.config.quote_currency}')
            return False

        if action == SignalAction.SELL and base_currency_amount == 0:
            self.log.debug(f'Action is sell but balance is 0 {self.config.base_currency}')
            return False

        #ticker = self.exchange.get_ticker()
        if action == SignalAction.BUY:
            self.log.info(f"*** Performing market buy of {quote_currency_amount} at {close}")
            self.exchange.market_buy(quote_currency_amount, close)
        elif action == SignalAction.SELL:
            self.log.info(f"*** Performing market sell of {base_currency_amount} at {close}")
            self.exchange.market_sell(base_currency_amount, close)

        return True



    def get_exchange(self, exchange):
        if exchange == 'coinbasepro':
            x = CoinBaseProExchange(self.market, self.config, self.log)
        if not self.config.live:
            x = DummyExchange(x, self.config, self.log)
        return x

    def render(self, df):
        filename = f'graphs/{self.config.base_currency}_trades.png'
        plt.close('all')
        plt.xticks(rotation=45)
        plt.plot(df.close, label='close')

        plt.legend()
        plt.ylabel('Close')
        for action in self.trades_to_render:
            plt.plot(action['time'], action['close'], 'g*' if action['action'] == SignalAction.BUY else 'r*', markersize=10, label='Buy' if action['action'] == SignalAction.BUY else 'Sell')

        plt.savefig(filename)
        self.log.critical(f'file:{filename}')


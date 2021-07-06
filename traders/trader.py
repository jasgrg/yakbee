from traders.trader_config import TraderConfig
from traders.exchanges.coinbase_pro_exchange import CoinBaseProExchange
from traders.signals.signal_action import SignalAction
from traders.exchanges.dummy_exchange import DummyExchange
from notifications.notification_service import NotificationService
import matplotlib.pyplot as plt


class Trader:
    def __init__(self, config, log, notify_service = None):
        self.last_calc_date = 0
        self.log = log
        self.notify_service = notify_service or NotificationService()
        self.config = TraderConfig(config, log)
        self.market = f'{self.config.base_currency}-{self.config.quote_currency}'
        self.exchange = self.get_exchange(config['exchange'])
        self.last_action = self.exchange.get_last_action()
        self.render_after_calc = True
        self.log.debug(f'{self.config.name} created')

    def calculate_and_trade(self, current_time):

        time_since_last_calc = current_time - self.last_calc_date

        if time_since_last_calc >= self.config.granularity:

            self.log.debug(f'{self.config.name} running calculations')
            self.last_calc_date = current_time

            historical_data = self.get_historical_data(current_time)

            last_order = self.exchange.get_last_order()

            if historical_data.shape[0] > 1:
                close = historical_data.tail(1).close.values[0]

                for strategy in self.config.buy_strategies:

                    action = strategy.get_action(historical_data, last_order)

                    if action == SignalAction.BUY and self.last_action != SignalAction.BUY:
                        high_threshold = historical_data.close.max() * 0.97

                        if self.config.buy_near_high or close < high_threshold:

                            self.log.debug('*** Strategy returned BUY ***')
                            self.last_action = SignalAction.BUY

                            if self.trade(SignalAction.BUY, close):
                                self.log.debug('*** Buy was successful ***')
                                if self.config.live:
                                    self.notify_service.notify(f'{self.config.name} bought at {close}')
                            break
                        else:
                            self.log.debug(f'Cannot buy near or above high : current price {close} : high threshold : {high_threshold}')

                for strategy in self.config.sell_strategies:

                    action = strategy.get_action(historical_data, last_order)

                    if action == SignalAction.SELL and self.last_action != SignalAction.SELL:

                        self.log.debug('*** Strategy returned SELLs ***')
                        last_buy_order = self.exchange.get_last_buy_order()

                        if self.config.sell_at_loss or last_buy_order is None or close > (float(last_buy_order['price']) + ((self.config.min_gain_to_sell / 100) * float(last_buy_order['price']))):

                            self.last_action = SignalAction.SELL

                            if self.trade(SignalAction.SELL, close):
                                self.log.debug('*** Sell was successful ***')
                                if self.config.live:
                                    self.notify_service.notify(f'{self.config.name} sold at {historical_data.tail(1).close.values[0]}')
                            break
                        else:
                            self.log.debug(f'Cannot sell at a loss : current price {close} : purchased price {last_buy_order["price"]} : target {(float(last_buy_order["price"]) + ((self.config.min_gain_to_sell / 100) * float(last_buy_order["price"])))}')

            if self.render_after_calc:
                try:
                    self.render(historical_data)
                    self.render_strategies()
                except Exception as ex:
                    # log and continue
                    self.log.warning(f'failed to render trades or strategies')

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

        if action == SignalAction.BUY:
            self.log.info(f"*** Performing market buy of {quote_currency_amount} at {close}")
            self.exchange.market_buy(quote_currency_amount, close)
        elif action == SignalAction.SELL:
            self.log.info(f"*** Performing market sell of {base_currency_amount} at {close}")
            self.exchange.market_sell(base_currency_amount, close)

        return True

    def get_exchange(self, exchange):
        x = self._get_base_exchange(exchange)
        if not self.config.live:
            x = DummyExchange(x, self.config, self.log)
        return x

    def render_strategies(self):
        for s in self.config.buy_strategies:
            s.render()
        for s in self.config.sell_strategies:
            s.render()

    def render(self, historical_data=None):

        if historical_data is None:
            historical_data = self.get_historical_data(self.last_calc_date)

        orders = self.exchange.get_filled_orders()
        min_date = historical_data.epoch.values[0]

        trades_to_render = [o for o in orders if o['date'].timestamp() > min_date]

        filename = f'graphs/{self.config.alias}_trades.png'
        plt.close('all')
        plt.xticks(rotation=45)
        plt.plot(historical_data.close, label='close')
        if len(orders) > 0 and len(trades_to_render) == 0 :
            if orders[0]['action'] == SignalAction.BUY:
                historical_data['last_buy'] = orders[0]['price']
                plt.plot(historical_data.last_buy, label='last buy', color='g')
            else:
                historical_data['last_sell'] = orders[0]['price']
                plt.plot(historical_data.last_sell, label='last sell', color='r')


        plt.legend()
        plt.ylabel('Close')
        for action in trades_to_render:
            plt.plot(action['date'], action['price'], 'g*' if action['action'] == SignalAction.BUY else 'r*', markersize=10, label='Buy' if action['action'] == SignalAction.BUY else 'Sell')

        plt.savefig(filename)
        self.notify_service.notify(f'file:{filename}')

    def _get_base_exchange(self, exchange):
        if exchange == 'coinbasepro':
            return CoinBaseProExchange(self.market, self.config, self.log)


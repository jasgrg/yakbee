import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time
import hmac
import hashlib
import base64
from numpy import floor
from traders.signals.signal_type import SignalAction
MAX_INTERVALS_PER_REQUEST = 300
INTERVALS_PRIOR_TO_START = 200
LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo

class CoinBaseProExchange():
    def __init__(self, market, config, log):
        self.api_url = config.auth['api_url']
        self.api_key = config.auth['api_key']
        self.api_secret = config.auth['api_secret']
        self.api_passphrase = config.auth['api_passphrase']

        self.market = market
        self.log = log
        self.base_url = 'https://api.pro.coinbase.com'
        self.orders = self.get_filled_orders()
        self.product = self._get_product()


    def get_historic_data(self, granularity, start_date_time: datetime = None, end_date_time: datetime = None):

        if granularity not in [60, 300, 900, 3600, 21600, 86400]:
            raise Exception(f'Invalid granularity {granularity}')

        if start_date_time is None or end_date_time is None:
            self.log.debug(f'Getting history | {granularity}')
            resp = requests.get(f'{self.base_url}/products/{self.market}/candles?granularity={granularity}')
            data = resp.json()
        else:
            # back up start date the number of intervals needed to start calculating
            start_date_time = start_date_time - timedelta(seconds=INTERVALS_PRIOR_TO_START * granularity)
            delta = end_date_time - start_date_time

            # do we need multiple requests?
            if delta.total_seconds() / granularity >= MAX_INTERVALS_PER_REQUEST:
                data = []
                cur_start_time = start_date_time
                cur_end_time = start_date_time + timedelta(seconds=MAX_INTERVALS_PER_REQUEST*granularity)
                while True:
                    self.log.debug(f'Getting history {cur_start_time} - {cur_end_time} | {granularity}')
                    resp = requests.get(
                        f'{self.base_url}/products/{self.market}/candles?granularity={granularity}&start={cur_start_time.isoformat()}&end={cur_end_time.isoformat()}')
                    data.extend(resp.json())
                    if cur_end_time >= end_date_time:
                        break
                    cur_start_time = cur_start_time + timedelta(seconds=MAX_INTERVALS_PER_REQUEST*granularity)
                    cur_end_time = cur_end_time + timedelta(seconds=MAX_INTERVALS_PER_REQUEST*granularity)
                    if cur_end_time > end_date_time:
                        cur_end_time = end_date_time


            else:
                self.log.debug(f'Getting history {start_date_time} - {end_date_time} | {granularity}')
                resp = requests.get(f'{self.base_url}/products/{self.market}/candles?granularity={granularity}&start={start_date_time.isoformat()}&end={end_date_time.isoformat()}')
                data = resp.json()

        data.sort(key=lambda x: x[0])

        dataframe = pd.DataFrame(data, columns=['epoch', 'low', 'high', 'open', 'close', 'volume'])
        #dataframe['date'] = dataframe.apply(lambda a: datetime.utcfromtimestamp(a["epoch"]), axis=1)
        dataframe['date'] = dataframe.apply(lambda a: datetime.fromtimestamp(a["epoch"], tz=LOCAL_TIMEZONE), axis=1)
        dataframe.set_index('date', inplace=True)
        #self.log.debug(dataframe)
        #dataframe.to_csv('datasets/six_months.csv')

        return dataframe

    def _get_product(self):
        resp = requests.get(f'{self.base_url}/products/{self.market}')
        if resp.status_code == 200:
            return resp.json()
        resp.raise_for_status()


    def _get_quote_increment(self):
        return self.product['quote_increment']

    def _get_base_increment(self):
        return self.product['base_increment']


    def _make_conform_to_increment(self, qty:float, increment: float) -> float:
        if '.' in str(increment):
            nb_digits = len(str(increment).split('.')[1])
        else:
            nb_digits = 0

        return floor(qty * 10 ** nb_digits) / 10 ** nb_digits


    def get_ticker(self):
        resp = requests.get(f'{self.base_url}/products/{self.market}/ticker')
        if resp.status_code == 200:
            resp_obj = resp.json()
            return (resp_obj['time'], float(resp_obj['price']))

        resp.raise_for_status()

    def __call__(self, request) -> requests.Request:
        timestamp = str(time.time())
        body = (request.body or b'').decode()
        message = f'{timestamp}{request.method}{request.path_url}{body}'
        hmac_key = base64.b64decode(self.api_secret)
        signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode()

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.api_passphrase,
            'Content-Type': 'application/json'
        })

        return request

    def get_available_amount(self, currency) -> float:
        return float(self.get_account(currency)[0]["available"])

    def get_account(self, currency):
        resp = requests.get(f'{self.api_url}/accounts', auth=self)
        if resp.status_code == 200:
            accounts = resp.json()
            return [acc for acc in accounts if acc['currency'] == currency]
        resp.raise_for_status()


    def market_buy(self, quote_quantity:float, close: float):
        funds = self._make_conform_to_increment(quote_quantity, self._get_quote_increment())

        order = {
            'product_id': self.market,
            'type': 'market',
            'side': 'buy',
            'funds': funds
        }

        self.log.debug(order)

        resp = requests.post(f'{self.base_url}/orders', json=order, auth=self)
        resp.raise_for_status()


    def market_sell(self, base_quantity, close: float):
        base_increment = self._get_base_increment()
        qty = self._make_conform_to_increment(base_quantity, base_increment)

        order = {
            'product_id': self.market,
            'type': 'market',
            'side': 'sell',
            'size': qty
        }

        resp = requests.post(f'{self.base_url}/orders', json=order, auth=self)
        resp.raise_for_status()

    def get_filled_orders(self):
        resp = requests.get(f'{self.api_url}/fills?product_id={self.market}', auth=self)
        if resp.status_code == 200:
            orders = resp.json()
            orders.sort(key=lambda o: o['created_at'])
            orders.reverse()
            return orders
        resp.raise_for_status()


    def get_orders(self):
        resp = requests.get(f'{self.api_url}/orders', auth=self) #?product_id={self.market}
        if resp.status_code == 200:
            orders = resp.json()
            orders.sort(key=lambda o: o['created_at'])
            orders.reverse()
            return orders
        resp.raise_for_status()

    def get_last_action(self):
        if len(self.orders) > 0:
            return SignalAction.BUY if self.orders[0]['side'] == 'buy' else SignalAction.SELL
        return SignalAction.WAIT


    def get_last_buy_order(self):
        orders = [o for o in self.orders if o['side'] == 'buy']
        return orders[0] if len(orders) > 0 else None

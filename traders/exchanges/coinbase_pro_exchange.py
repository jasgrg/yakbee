import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time
import hmac
import hashlib
import base64
from numpy import floor
from traders.signals.signal_action import SignalAction

MAX_INTERVALS_PER_REQUEST = 300
INTERVALS_PRIOR_TO_START = 200


class CoinBaseProExchange():
    def __init__(self, market, config, log):
        self.api_url = config.auth['api_url']
        self.api_key = config.auth['api_key']
        self.api_secret = config.auth['api_secret']
        self.api_passphrase = config.auth['api_passphrase']

        self.market = market
        self.log = log
        self.base_url = 'https://api.pro.coinbase.com'
        self.product = self._get_product()
        self.filled_orders = None
        self.last_filled_orders_fetch = None

        self.accounts = None
        self.last_accounts_fetch = None

    def get_historic_data(self, granularity, start_date_time: datetime = None, end_date_time: datetime = None, retry=0):
        if granularity not in [60, 300, 900, 3600, 21600, 86400]:
            raise Exception(f'Invalid granularity {granularity}')

        try:

            if start_date_time is None or end_date_time is None:
                self.log.debug(f'Getting history | {granularity}')
                resp = requests.get(f'{self.base_url}/products/{self.market}/candles?granularity={granularity}')
                resp.raise_for_status()
                data = resp.json()
            else:
                start_date_time = start_date_time.replace(tzinfo=None)
                end_date_time = end_date_time.replace(tzinfo=None)
                # back up start date the number of intervals needed to start calculating
                start_date_time = start_date_time - timedelta(seconds=INTERVALS_PRIOR_TO_START * granularity)
                delta = end_date_time - start_date_time

                # do we need multiple requests?
                if delta.total_seconds() / granularity >= MAX_INTERVALS_PER_REQUEST:
                    data = []
                    cur_start_time = start_date_time
                    cur_end_time = start_date_time + timedelta(seconds=MAX_INTERVALS_PER_REQUEST * granularity)
                    while True:
                        self.log.debug(f'Getting history {cur_start_time} - {cur_end_time} | {granularity}')
                        resp = requests.get(
                            f'{self.base_url}/products/{self.market}/candles?granularity={granularity}&start={cur_start_time.isoformat()}&end={cur_end_time.isoformat()}')
                        resp.raise_for_status()
                        data.extend(resp.json())
                        if cur_end_time >= end_date_time:
                            break
                        cur_start_time = cur_start_time + timedelta(seconds=MAX_INTERVALS_PER_REQUEST * granularity)
                        cur_end_time = cur_end_time + timedelta(seconds=MAX_INTERVALS_PER_REQUEST * granularity)
                        if cur_end_time > end_date_time:
                            cur_end_time = end_date_time

                else:
                    self.log.debug(f'Getting history {start_date_time} - {end_date_time} | {granularity}')
                    resp = requests.get(
                        f'{self.base_url}/products/{self.market}/candles?granularity={granularity}&start={start_date_time.isoformat()}&end={end_date_time.isoformat()}')
                    resp.raise_for_status()
                    data = resp.json()

            data.sort(key=lambda x: x[0])

            dataframe = pd.DataFrame(data, columns=['epoch', 'low', 'high', 'open', 'close', 'volume'])
            dataframe['date'] = dataframe.apply(lambda a: datetime.fromtimestamp(a["epoch"], tz=timezone.utc), axis=1)
            dataframe.set_index('date', inplace=True)
            return dataframe

        except Exception as ex:
            if retry < 3:
                self.log.debug(f'getting historic data failed, retry {retry}')
                return self.get_historic_data(granularity, start_date_time, end_date_time, retry + 1)
            else:
                raise

    def _get_product(self):
        resp = requests.get(f'{self.base_url}/products/{self.market}')
        if resp.status_code == 200:
            return resp.json()
        self.log.error(f'Status {resp.status_code} : {resp.text}')
        resp.raise_for_status()

    def _get_quote_increment(self):
        return self.product['quote_increment']

    def _get_base_increment(self):
        return self.product['base_increment']

    def _make_conform_to_increment(self, qty: float, increment: float) -> float:
        if '.' in str(increment):
            nb_digits = len(str(increment).split('.')[1])
        else:
            nb_digits = 0

        return floor(qty * 10 ** nb_digits) / 10 ** nb_digits

    def get_ticker(self):
        resp = requests.get(f'{self.base_url}/products/{self.market}/ticker')
        if resp.status_code == 200:
            resp_obj = resp.json()
            return resp_obj['time'], float(resp_obj['price'])
        self.log.error(f'Status {resp.status_code} : {resp.text}')
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

    def get_accounts(self, retry=0):
        self.log.debug('Getting accounts')

        if self.accounts is not None:
            seconds = datetime.now().timestamp() - self.last_accounts_fetch
            if seconds < 30:
                self.log.debug(f'Cache hit on accounts')
                return self.accounts

        resp = requests.get(f'{self.api_url}/accounts', auth=self)
        if resp.status_code == 200:
            self.accounts = resp.json()
            self.last_accounts_fetch = datetime.now().timestamp()
            return self.accounts
        elif retry < 3:
            self.log.debug(f'Getting account failed {resp.status_code} retrying {retry}')
            return self.get_accounts(retry + 1)
        else:
            self.log.error(f'Status {resp.status_code} : {resp.text}')
            resp.raise_for_status()

    def get_account(self, currency):
        accounts = self.get_accounts()
        return [acc for acc in accounts if acc['currency'] == currency]

    def market_buy(self, quote_quantity: float, close: float, retry=0):

        funds = self._make_conform_to_increment(quote_quantity, self._get_quote_increment())

        order = {
            'product_id': self.market,
            'type': 'market',
            'side': 'buy',
            'funds': funds
        }

        self.log.debug(order)

        resp = requests.post(f'{self.base_url}/orders', json=order, auth=self)
        if resp.status_code == 200:
            return
        elif retry < 3:
            self.log.debug(f'market buy failed, retrying {retry}')
            self.market_buy(quote_quantity, close, retry + 1)
        else:
            self.log.error(f'Status {resp.status_code} : {resp.text}')
            resp.raise_for_status()


    def market_sell(self, base_quantity, close: float, retry=0):
        base_increment = self._get_base_increment()
        qty = self._make_conform_to_increment(base_quantity, base_increment)

        order = {
            'product_id': self.market,
            'type': 'market',
            'side': 'sell',
            'size': qty
        }

        resp = requests.post(f'{self.base_url}/orders', json=order, auth=self)
        if resp.status_code == 200:
            return
        elif retry < 3:
            self.log.debug(f'market sell failed, retrying {retry}')
            self.market_sell(base_quantity, close, retry+1)
        else:
            self.log.error(f'Status {resp.status_code} : {resp.text}')
            resp.raise_for_status()

    def get_filled_orders(self, retry=0):
        self.log.debug('Getting filled orders')

        if self.filled_orders is not None:
            seconds = datetime.now().timestamp() - self.last_filled_orders_fetch
            if seconds < 30:
                self.log.debug(f'Cache hit on filled orders')
                return self.filled_orders

        resp = requests.get(f'{self.api_url}/fills?product_id={self.market}', auth=self)
        if resp.status_code == 200:
            orders = resp.json()
            orders.sort(key=lambda o: o['created_at'])
            orders.reverse()
            self.filled_orders = [{
                'date': pd.to_datetime(o['created_at']),
                'price': float(o['price']),
                'size': float(o['size']),
                'fee': float(o['fee']),
                'action': SignalAction.BUY if o['side'] == 'buy' else SignalAction.SELL
            } for o in orders]
            self.last_filled_orders_fetch = datetime.now().timestamp()
            return self.filled_orders

        elif retry < 2:
            self.log.debug(f'Filled orders failed {resp.status_code} trying again {retry}')
            return self.get_filled_orders(retry + 1)
        else:
            self.log.error(f'Status {resp.status_code} : {resp.text}')
            resp.raise_for_status()

    def get_orders(self):
        resp = requests.get(f'{self.api_url}/orders', auth=self)  # ?product_id={self.market}
        if resp.status_code == 200:
            orders = resp.json()
            orders.sort(key=lambda o: o['created_at'])
            orders.reverse()
            return orders
        self.log.error(f'Status {resp.status_code} : {resp.text}')
        resp.raise_for_status()

    def get_last_action(self):
        self.log.debug('Getting last action')
        orders = self.get_filled_orders()
        if len(orders) > 0:
            return orders[0]['action']
        return SignalAction.WAIT

    def get_last_order(self):
        self.log.debug('Getting last order')
        orders = self.get_filled_orders()
        if len(orders) > 0:
            return orders[0]
        return None

    def get_last_buy_order(self):
        self.log.debug('Getting last buy order')
        orders = self.get_filled_orders()
        orders = [o for o in orders if o['action'] == SignalAction.BUY]
        return orders[0] if len(orders) > 0 else None

    def get_min_buy_amount(self):
        return float(self.product['min_market_funds'])

    def get_min_sell_amount(self):
        return float(self.product['base_min_size'])

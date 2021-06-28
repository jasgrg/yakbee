## Yakbee 

### About
Yakbee is yet another crypto-currency trading bot. It can trade in an arbitrary number of markets with a unique
 configuration for each market. When I set out to build this bot my goal was to build it as modular 
as possible so that adding new signals and strategies did not require change to the core code.

#### Prerequisites
- Python 3.7 - <https://installpython3.com>
- Pip3 - <https://pip.pypa.io>

#### Installation
    % git clone https://github.com/jasgrg/yakbee.git
    % cd yakbee
    % pip3 install -r requirements.txt
    
##### Alternate installation for raspberry pi
If you want to run yakbee on a raspberry pi you might need to install the dependency a bit differently.

    % git clone https://github.com/jasgrg/yakbee.git
    % sudo apt-get install python3-pandas python3-matplotlib
    % pip3 install requests python-telegram-bot
 
#### Configuration

The configuration for yakbee is found in a <code>config.json</code> file in the root directory of the project. This file
This file is not in source control so before running yakbee you'll need to create it.

##### Sample <code>config.json</code>

    {
        "traders": [
            {
                "name": "BTC-USD on coinbase pro",
                "live" : 0,
                "exchange": "coinbasepro",
                "auth": {
                    "api_url": "https://api.pro.coinbase.com",
                    "api_key": "<removed>",
                    "api_secret": "<removed>",
                    "api_passphrase": "<removed>"
                },
                "config" : {
                    "base_currency" : "BTC",
                    "quote_currency" : "USD",
                    "granularity" : 300,
                    "sell_at_loss": "false",
                    "buy_strategies": [["exponential_moving_average_slope"]],
                    "sell_strategies": [["exponential_moving_average_slope"]]
                }
            }
        ],

        "sim": {
              "simulation": true,
              "sim_start_date": "2021-06-24 00:00:00",
              "sim_end_date": "2021-06-27 00:00:00"
        },
        "telegram": {
            "token": "<removed>",
            "client_id": "<removed>"
        },
        "log": {
            "loglevel": "INFO"
        }
    }

##### Configuration Breakdown

The <code>traders</code> section is the only required section in the configuration. <code>Traders</code> specifies a 
list of markets you want the bot to trade in and the configuration associated with each market.

- <code>name</code> Just for logging to specify what trader is emitting the log entries.
- <code>live</code> 0 means the bot will run in simulation mode and perform theoretical trades. 1 means the bot will 
trade with live funds.
- <code>exchange</code> specifies what online exchange to use. Current options are <code>coinbasepro</code> only.
- <code>auth</code> authorization properties specific to the specified exchange.
- Trader specific configuration:
  - <code>base_currency</code> the desired base currency to trade.
  - <code>quote_currency</code> the desired quote currency to trade. The combination of base currency and quote currency 
  are what define the "market".
  - <code>granularity</code> most (*all* at the current time) trading signals will look at the base currency's price at
  at a specified granularity (1m, 5m, 15m, 1hr, etc) to determine trading actions. These intervals are usually graphically
  represented as [candlesticks](https://www.investopedia.com/trading/candlestick-charting-what-is-it/).
  - <code>sellatloss</code> when <code>false</code> the bot will not execute a sell if the current value is less than the
  previous purchase value. This can be good or bad depending on your strategy. Sometimes a short term loss can result in a long
  term gain, but not always. Trade with care.
  - <code>buy_strategies</code> is a two-dimensional array of strings. Each child array is a strategy. Each string within 
  the strategy represents a signal. During the trading cycle the bot will consult each strategy on whether it determines
  a buy action or a sell action. If *any* strategy returns a buy action then a buy will be executed. In order for a strategy
  to return a buy action, *all* of the signals must return a buy action.
  - <code>sell_strategies</code> if not strategies return a buy action, then the sell strategies are consulted. If *any*
  sell strategy returns a sell action then a sell is executed. In order for a strategy to return a sell action, *all* of the 
  signals within the strategy must return a sell signal.

#### Execution

    % python3 yakbee.py
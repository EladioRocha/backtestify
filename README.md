## Table of contents

- [Table of contents](#table-of-contents)
- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction
While there are already backtesting tools available, I aimed to create a tool that allows for more accurate backtesting specifically for Contract for Difference (CFD). My vision was to create a comprehensive tool that takes care of the entire backtesting process, where the trader can focus solely on strategy formulation and testing new strategies without needing to invest time in coding. This tool is envisioned to be user-friendly and fully open-source, similar to other strategy analysis builders available on the market, but with the added benefit of being completely free.

While platforms like MetaTrader 5 allow for backtesting strategies using technical indicators, they often fall short when it comes to applying advanced techniques such as machine learning. Such processes can be complicated and tedious. By creating a backtester directly in Python, this process is significantly simplified, and it also opens up the possibility of utilizing all kinds of existing Python modules.

## Installation
pip install backtestify

## Usage
A simple example of how to use the package is shown below. More examples will be added in the future in the examples folder.

```python
import pandas as pd
from backtestify import Strategy, SignalEvent, SignalType, Backtester, Account, CFD, InstrumentType
import MetaTrader5 as mt5
import datetime
import talib as ta

def get_asset_info_mt5(symbol, timeframe=mt5.TIMEFRAME_D1, n=1000):
    mt5.initialize()
    utc_from = datetime.datetime.now()
    rates = mt5.copy_rates_from(symbol, timeframe, utc_from, n)
    rates_frame = pd.DataFrame(rates)

    columns = ['time', 'open', 'high', 'low', 'close', 'tick_volume']
    rates_frame = rates_frame[columns]

    rates_frame = rates_frame.set_index('time')
    rates_frame.rename(columns={'tick_volume': 'volume'}, inplace=True)
    rates_frame.index.name = 'timestamp'

    rates_frame['swap_long'] = -7.84 # This is the swap rate for SPX500. This can be found in the Market Watch window in MetaTrader 5 this could be different for a specific broker or instrument and take in consideration that this could be different depending on the day of the week.
    rates_frame['swap_short'] = 4.26

    return rates_frame

class RSIStrategy(Strategy):
    def __init__(self, market_info, rsi_period):
        self.rsi_period = rsi_period
        self.previous_trade_signal = None
        market_info["rsi"] = ta.RSI(market_info["close"], timeperiod=rsi_period)

        super().__init__(market_info)

    def on_tick(self, history):
        try:

            current = history.iloc[-1]

            if current["rsi"] is None:
                return

            if current["rsi"] < 30 and self.previous_trade_signal != SignalType.BUY:
                self.previous_trade_signal = SignalType.BUY
                return [
                    SignalEvent(signal=SignalType.EXIT),
                    SignalEvent(signal=SignalType.BUY)
                ]

            if current["rsi"] > 70 and self.previous_trade_signal != SignalType.SELL:
                self.previous_trade_signal = SignalType.SELL
                return [
                    SignalEvent(signal=SignalType.EXIT),
                    SignalEvent(signal=SignalType.SELL)
                ]

        except Exception as e:
            pass

cfd = CFD(
    instrument_type=InstrumentType.STOCK,
    lot_size=1,
    entry_lots=1,
    commission=0,
    point_value=1,
    leverage=100,
    point=0.01,
    spread=5,
    period=mt5.TIMEFRAME_D1,
    pips=0.01,
)
df = get_asset_info_mt5("SPX500")

sma = RSIStrategy(df, 14)
account = Account(10000)
backtester = Backtester(sma, cfd, account)
backtester.run()

backtester.results
```

## Contributing

For any bug reports or recommendations, please visit our [issue tracker](https://github.com/EladioRocha/backtestify/issues) and create a new issue. If you're reporting a bug, it would be great if you can provide a minimal reproducible example.

Thank you for your contribution!

## License
[Apache 2.0](https://choosealicense.com/licenses/apache-2.0/)
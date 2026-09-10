# Backtestify

An experimental **event-driven Python backtester** with CFD instrument parameters, strategy signals, account state, and trade records. It is designed for source-level strategy experiments; there is no visual strategy builder or live execution adapter in the package.

## Install this checkout

```sh
git clone https://github.com/EladioRocha/backtestify.git
cd backtestify
python -m pip install -e .
```

[setup.py](setup.py) declares version `0.1.6` and pandas as the runtime dependency. The examples below use the source checkout; a package-index release may differ.

## Offline example

This synthetic three-bar example needs no broker connection or external market data:

```python
import pandas as pd
from backtestify import (
    Account, Backtester, CFD, InstrumentType,
    SignalEvent, SignalType, Strategy,
)

prices = pd.DataFrame({
    "open": [100.0, 101.0, 102.0],
    "high": [101.0, 102.0, 103.0],
    "low": [99.0, 100.0, 101.0],
    "close": [100.5, 101.5, 102.5],
}, index=pd.date_range("2024-01-01", periods=3, name="timestamp"))

class BuyOnce(Strategy):
    def on_tick(self, history):
        if len(history) == 1:
            return SignalEvent(signal=SignalType.BUY)
        return None

instrument = CFD(
    instrument_type=InstrumentType.STOCK,
    lot_size=1, entry_lots=1, commission=0,
    point_value=1, leverage=1, period=1,
    point=0.01, spread=0, pips=0.01,
)
backtester = Backtester(BuyOnce(prices), instrument, Account(10000))
backtester.run()
print(backtester.results)
```

The strategy machinery adds an exit signal on the last bar. The example is a code demonstration with arbitrary instrument settings, not a realistic performance study.

## Data and strategy contract

- Subclass `Strategy` and implement `on_tick(history)`. History includes the current bar.
- Return a `SignalEvent`, a list of events, or `None`.
- Provide `open`, `high`, `low`, and `close` columns. `volume` is optional.
- Provide a `timestamp` column or an index named `timestamp`.
- Optional `swap_long`, `swap_short`, and `symbol` columns populate event metadata; missing swaps default to zero.
- Build fresh strategy, account, and backtester objects for independent runs because event and trade state accumulate.

## Code map

| File | Responsibility |
| --- | --- |
| [backtestify/strategy.py](backtestify/strategy.py) | Iterate price history and enrich signals. |
| [backtestify/backtester.py](backtestify/backtester.py) | Execute events and expose trade results. |
| [backtestify/cfd.py](backtestify/cfd.py) | Instrument costs and position parameters. |
| [backtestify/trade_executor.py](backtestify/trade_executor.py) | Position opening, closing, and price calculations. |
| [backtestify/account.py](backtestify/account.py) | Account balance and equity. |

The [historical MetaTrader example](docs/metatrader-example.md) is preserved separately because it needs extra dependencies and a terminal connection.

## Limitations and validation

There is no automated test suite. Empty trade results currently fail when setting the result index, and some stop-loss/take-profit branches reference attributes not initialized by `TradeExecutor`. The offline example does not exercise those branches. Review execution-price assumptions, current-bar information, costs, and risk handling before interpreting results.

Report issues with a minimal dataset and expected trade sequence in the [issue tracker](https://github.com/EladioRocha/backtestify/issues). Licensed under [Apache 2.0](LICENSE).

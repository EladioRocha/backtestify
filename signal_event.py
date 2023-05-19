from event import Event
from event_type import EventType
from signal_type import SignalType
from trade_calculator import TradeCalculator
from trade import Trade

class SignalEvent(Event):
    """
    The SignalEvent class is a subclass of the Event class, representing a trading signal event.
    It contains information about a trading signal, such as the symbol, timestamp, and signal type (buy/sell).
    Additionally, it can store price and volume data for further analysis or strategy implementation.

    Attributes:
        signal (str): A string representing the signal type ('BUY', 'SELL', 'EXIT', etc.).
        symbol (str, optional): A string representing the ticker symbol of the security involved in the event. Defaults to None.
        timestamp (datetime.datetime, optional): A datetime object representing the time at which the event occurred. Defaults to None.
        take_profit (float, optional): The price at which to take profit for the trade. Defaults to None.
        stop_loss (float, optional): The price at which to stop loss for the trade. Defaults to None.
        open_price (float, optional): The open price of the security at the time of the signal. Defaults to None.
        high_price (float, optional): The high price of the security at the time of the signal. Defaults to None.
        low_price (float, optional): The low price of the security at the time of the signal. Defaults to None.
        close_price (float, optional): The close price of the security at the time of the signal. Defaults to None.
        volume (int, optional): The trading volume of the security at the time of the signal. Defaults to None.
        swap (float, optional): The swap value for the trade. Defaults to None.
    """

    def __init__(self, signal, symbol=None, timestamp=None, take_profit=None, stop_loss=None, previous_event=None):
        """
        Initializes a new instance of the SignalEvent class.

        Args:
            signal (str): A string representing the signal type ('BUY', 'SELL', 'EXIT', etc.).
            symbol (str, optional): A string representing the ticker symbol of the security involved in the event. Defaults to None.
            timestamp (datetime.datetime, optional): A datetime object representing the time at which the event occurred. Defaults to None.
            take_profit (float, optional): The price at which to take profit for the trade. Defaults to None.
            stop_loss (float, optional): The price at which to stop loss for the trade. Defaults to None.
        """
        super().__init__(event_type=EventType.SIGNAL, timestamp=timestamp, symbol=symbol)
        self.signal = signal
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.previous_event = previous_event
        self.open_price = None
        self.high_price = None
        self.low_price = None
        self.close_price = None
        self.volume = None
        self.swap = None

    def execute(self, instrument):
        pass

    def __str__(self):
        return "Event: %s, Timestamp: %s, Symbol: %s, Signal: %s, Take Profit: %s, Stop Loss: %s" % (self.event_type, self.timestamp, self.symbol, self.signal, self.take_profit, self.stop_loss)

    def __repr__(self):
        return str(self)

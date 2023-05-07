class Event:
    """
    The Event class is a base class that represents an abstract event in a trading system.
    It can be extended by other classes to represent specific types of events (e.g., MarketEvent, SignalEvent, OrderEvent).

    Attributes:
        event_type (str): A string describing the type of event.
        timestamp (datetime.datetime, optional): A datetime object representing the time at which the event occurred. Defaults to None.
        symbol (str, optional): A string representing the ticker symbol of the security involved in the event. Defaults to None.
    """

    def __init__(self, event_type, timestamp=None, symbol=None):
        """
        Initializes a new instance of the Event class.

        Args:
            event_type (str): A string describing the type of event.
            timestamp (datetime.datetime, optional): A datetime object representing the time at which the event occurred. Defaults to None.
            symbol (str, optional): A string representing the ticker symbol of the security involved in the event. Defaults to None.
        """
        self.timestamp = timestamp
        self.event_type = event_type
        self.symbol = symbol

    def execute(self, backtester):
        """
        This method is a placeholder for executing the event logic.
        It should be overridden by child classes to provide specific implementation.

        Args:
            backtester (Backtester): An instance of the backtester that will be used to execute the event logic.

        Raises:
            NotImplementedError: If the method is not implemented by the child class.
        """
        raise NotImplementedError("The execute() method is not implemented.")

    def __str__(self):
        return "Event: %s, Timestamp: %s, Symbol: %s" % (self.event_type, self.timestamp, self.symbol)
    
    def __repr__(self):
        return str(self)
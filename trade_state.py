class TradeState:
    """
    The TradeState class represents the current state of a trade in a trading system.
    It holds information about the trade's balance, equity, signal event, and other relevant data.

    Attributes:
        balance (float): The initial account balance for the trade.
        equity (float): The account equity, initially set to the balance.
        state (str, optional): The current state of the trade (e.g., 'OPEN', 'CLOSED', etc.). Defaults to None.
        size (float): The size of the security being traded. Defaults to 0.
        unrealized_profit (float): The current unrealized profit for the trade. Defaults to 0.
        realized_profit (float): The realized profit for the trade. Defaults to 0.
    """

    def __init__(
        self, 
        balance,
        size=0, 
        signal=None, 
        stop_loss=0, 
        take_profit=0, 
        adjusted_price=0,
        entry_price=0,
    ):
        """
        Initializes a new instance of the TradeState class.

        Args:
            balance (float): The initial account balance for the trade.
            signal_event (SignalEvent): An instance of the SignalEvent class associated with the trade.
        """
        self.timestamp = None
        self.adjusted_price = adjusted_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.balance = balance
        self.equity = balance
        self.signal = signal
        self.size = size
        self.unrealized_profit = 0
        self.realized_profit = 0
        self.entry_price = entry_price

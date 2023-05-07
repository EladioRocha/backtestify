class TradeState:
    """
    The TradeState class represents the current state of a trade in a trading system.
    It holds information about the trade's balance, equity, signal event, and other relevant data.

    Attributes:
        signal_event (SignalEvent): An instance of the SignalEvent class associated with the trade.
        balance (float): The initial account balance for the trade.
        equity (float): The account equity, initially set to the balance.
        state (str, optional): The current state of the trade (e.g., 'OPEN', 'CLOSED', etc.). Defaults to None.
        amount (float): The amount of the security being traded. Defaults to 0.
        unrealized_profit (float): The current unrealized profit for the trade. Defaults to 0.
        realized_profit (float): The realized profit for the trade. Defaults to 0.
    """

    def __init__(self, balance, signal_event):
        """
        Initializes a new instance of the TradeState class.

        Args:
            balance (float): The initial account balance for the trade.
            signal_event (SignalEvent): An instance of the SignalEvent class associated with the trade.
        """
        self.signal_event = signal_event
        self.balance = balance
        self.equity = balance
        self.state = None
        self.amount = 0
        self.unrealized_profit = 0
        self.realized_profit = 0

    def __str__(self):
        return "Trade State: %s, Balance: %s, Equity: %s, Amount: %s, Unrealized Profit: %s, Realized Profit: %s" % (self.state, self.balance, self.equity, self.amount, self.unrealized_profit, self.realized_profit)

    def __repr__(self):
        return str(self)

from signal_type import SignalType

class TradeState:
    """
    The TradeState class represents the current_trade_state state of a trade in a trading system.
    It holds information about the trade's balance, equity, signal event, and other relevant data.

    Attributes:
        balance (float): The initial account balance for the trade.
        equity (float): The account equity, initially set to the balance.
        state (str, optional): The current_trade_state state of the trade (e.g., 'OPEN', 'CLOSED', etc.). Defaults to None.
        size (float): The size of the security being traded. Defaults to 0.
        unrealized_profit (float): The current_trade_state unrealized profit for the trade. Defaults to 0.
        realized_profit (float): The realized profit for the trade. Defaults to 0.
    """

    def __init__(
        self, 
        balance,
        initial_timestamp=None,
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
        self.initial_timestamp = initial_timestamp
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

    @classmethod
    def copy_and_update(cls, current_trade_state, swap_long, swap_short, point, instrument_type):
        if current_trade_state.signal is None:
            return cls(balance=current_trade_state.balance)

        swap = -swap_long if current_trade_state.signal == SignalType.BUY else swap_short
        adjusted_price = TradeState.get_price_by_instrument_type(current_trade_state.adjusted_price, swap, point, instrument_type)

        return cls(
            balance=current_trade_state.balance,
            size=current_trade_state.size,
            signal=current_trade_state.signal,
            stop_loss=current_trade_state.stop_loss,
            take_profit=current_trade_state.take_profit,
            adjusted_price=adjusted_price
        )
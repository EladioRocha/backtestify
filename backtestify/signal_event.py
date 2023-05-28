from backtestify.event import Event
from backtestify.event_type import EventType
from backtestify.signal_type import SignalType
from backtestify.trade_executor import TradeExecutor
from backtestify.trade_state import TradeState

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
        self.swap_long = None
        self.swap_short = None

    def execute(self, instrument, current_trade_state, balance, current_bar):
        if current_bar == 0:
            return TradeState(balance)
        
        trade = None
        is_trade_open = False

        trade_state = TradeState.copy_and_update(
            current_trade_state=current_trade_state,
            swap_long=self.swap_long,
            swap_short=self.swap_short,
            point=instrument.point,
        )

        stop_loss, use_stop_loss = self.get_stop_loss(trade_state.stop_loss)
        take_profit, use_take_profit = self.get_take_profit(trade_state.take_profit)
        stop_loss_pips = self.calculate_stop_loss(use_stop_loss, stop_loss, instrument.pips)
        take_profit_pips = self.calculate_take_profit(use_take_profit, take_profit, instrument.pips)
        
        trade_executor = TradeExecutor(
            timestamp=self.timestamp,
            current_bar=current_bar,
            equity=trade_state.equity,
            margin=instrument.margin,
            currency_ratio=instrument.currency_ratio,
        )

        if trade_state.signal is None:
            if trade_state.equity <= instrument.required_margin and (self.signal == SignalType.BUY or self.signal == SignalType.SELL):
                return trade_state
            
            trade = trade_executor.open_trade(
                trade_state=trade_state,
                commission=instrument.commission,
                position_size=instrument.position_size,
                event_signal=self.signal,
                use_stop_loss=use_stop_loss,
                stop_loss_pips=stop_loss_pips,
                use_take_profit=use_take_profit,
                take_profit_pips=take_profit_pips,
                open_price=self.open_price,
                spread_points=instrument.spread_points
            )

        if trade_state.signal in [SignalType.BUY, SignalType.SELL, SignalType.EXIT]:
            close_buy_position, close_sell_position = trade_executor.should_close_position(
                trade_state_signal=trade_state.signal,
                event_signal=self.signal,
                use_stop_loss=use_stop_loss,
                stop_loss=stop_loss,
                use_take_profit=use_take_profit,
                take_profit=take_profit,
                spread_points=instrument.spread_points,
                open_price=self.open_price
            )

            if (trade_state.signal == SignalType.BUY and close_buy_position) or (trade_state.signal == SignalType.SELL and close_sell_position):
                trade = trade_executor.close_trade(
                    trade_state=trade_state,
                    trade_state_signal=trade_state.signal,
                    open_price=self.open_price,
                    spread_point=instrument.spread_points,
                    position_size=instrument.position_size,
                    trade_state_price=trade_state.adjusted_price,
                    event_signal=self.signal,
                )
            else:
                if use_stop_loss:
                    trade = trade_executor.execute_stop_loss(
                        is_trade_open=is_trade_open,
                        trade_state_signal=trade_state.signal,
                        trade_state=trade_state,
                        open_price=self.open_price,
                        low_price=self.low_price,
                        high_price=self.high_price,
                        close_price=self.close_price,
                        spread_points=instrument.spread_points,
                        previous_close_price=self.previous_event.close_price,
                        commission=instrument.commission,
                        position_size=instrument.position_size,
                        point_value=instrument.point_value,
                        event_signal=self.signal
                    )

                if use_take_profit:
                    trade = trade_executor.execute_take_profit(
                        is_trade_open=is_trade_open,
                        trade_state_signal=trade_state.signal,
                        trade_state=trade_state,
                        open_price=self.open_price,
                        low_price=self.low_price,
                        high_price=self.high_price,
                        close_price=self.close_price,
                        spread_points=instrument.spread_points,
                        previous_close_price=self.previous_event.close_price,
                        commission=instrument.commission,
                        position_size=instrument.position_size,
                        point_value=instrument.point_value,
                        event_signal=self.signal,
                    )

            trade_state = self.update_unrealized_profit(trade_state, instrument, self.close_price)

        return trade_state, trade

    def get_stop_loss(self, stop_loss):
        use_stop_loss = False
        stop_loss = 0

        if stop_loss > 0 or self.stop_loss is not None:
            use_stop_loss = True
            if stop_loss > 0:
                stop_loss = stop_loss
            elif self.stop_loss is not None:
                stop_loss = self.stop_loss

        return stop_loss, use_stop_loss
    
    def get_take_profit(self, take_profit):
        use_take_profit = False
        take_profit = 0

        if take_profit > 0 or self.take_profit is not None:
            use_take_profit = True
            if take_profit > 0:
                take_profit = take_profit
            elif self.take_profit is not None:
                take_profit = self.take_profit

        return take_profit, use_take_profit

    def calculate_take_profit(self, use_take_profit, take_profit, pips):
        return take_profit * pips if use_take_profit else 0
    
    def calculate_stop_loss(self, use_stop_loss, stop_loss, pips):
        return stop_loss * pips if use_stop_loss else 0

    def update_unrealized_profit(self, trade_state, instrument, close_price):
        if trade_state.signal is None:
            return trade_state
        
        current_close_price = close_price + (instrument.spread_points if trade_state.signal == SignalType.SELL else 0)
        floating_profit = (
            instrument.position_size
            * (current_close_price - trade_state.adjusted_price if trade_state.signal == SignalType.BUY else trade_state.adjusted_price - current_close_price)
            * instrument.point_value
            * instrument.currency_ratio
        )
        trade_state.unrealized_profit = floating_profit
        trade_state.equity = trade_state.balance + floating_profit

        return trade_state

    def __str__(self):
        return "Event: %s, Timestamp: %s, Symbol: %s, Signal: %s, Take Profit: %s, Stop Loss: %s" % (self.event_type, self.timestamp, self.symbol, self.signal, self.take_profit, self.stop_loss)

    def __repr__(self):
        return str(self)

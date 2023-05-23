from signal_type import SignalType
from trade import Trade

class TradeExecutor:
    def __init__(self, timestamp, current_bar, equity, margin, currency_ratio):
        self.timestamp = timestamp
        self.current_bar = current_bar
        self.insufficient_equity = equity <= margin * currency_ratio

    def open_trade(
        self, 
        trade_state, 
        comission, 
        position_size, 
        event_signal,
        use_stop_loss,
        stop_loss_pips,
        use_take_profit,
        take_profit_pips,
        open_price,
        spread_points
    ):
        trade_state.size = position_size
        trade_state.signal = event_signal
        trade_state.adjusted_price = open_price + (spread_points if event_signal == SignalType.BUY else 0)
        trade_state.stop_loss = self.calculate_stop_loss(
            use_stop_loss,
            event_signal, 
            open_price, 
            stop_loss_pips, 
            spread_points
        )
        trade_state.take_profit = self.calculate_take_profit(
            use_take_profit,
            event_signal, 
            open_price, 
            take_profit_pips, 
            spread_points
        )
        trade_state.balance -= comission
        trade_state.equity = trade_state.balance

        trade = Trade(
            timestamp=self.timestamp,
            bar=self.current_bar,
            signal=event_signal,
            size=position_size * (1 if event_signal == SignalType.BUY else -1),
            price=trade_state.adjusted_price,
            profit=0,
            balance=trade_state.balance,
            stop_loss=trade_state.stop_loss,
            take_profit=trade_state.take_profit
        )

        return trade

    def calculate_stop_loss(self, use_stop_loss, event_signal, open_price, stop_loss_pips, spread_points):
        if not use_stop_loss:
            return 0

        if SignalType.BUY == event_signal:
            return open_price - stop_loss_pips
        else:
            return open_price + spread_points + stop_loss_pips

    def calculate_take_profit(self, use_take_profit, event_signal, open_price, take_profit_pips, spread_points):
        if not use_take_profit:
            return 0
        
        if SignalType.BUY == event_signal:
            return open_price + take_profit_pips
        else:
            return open_price + spread_points - take_profit_pips

    def should_close_position(self, trade_state_signal, event_signal, use_stop_loss, stop_loss, use_take_profit, take_profit, spread_points, open_price):
        if trade_state_signal is None:
            return False, False
        
        def should_close_buy_position():
            if self.insuficient_equity:
                return True, False
            
            if trade_state_signal == SignalType.BUY:
                return (
                    # Verify if the stop loss was reached
                    (use_stop_loss and stop_loss >= open_price) or
                    # Verify if the take profit was reached
                    (use_take_profit and take_profit <= open_price) 
                )
            
            return False, False
        
        def should_close_sell_position():
            if self.insuficient_equity:
                return False, True
            
            if trade_state_signal == SignalType.SELL:
                return (
                    (use_stop_loss and stop_loss <= (open_price + spread_points)) or
                    (use_take_profit and take_profit >= (open_price + spread_points))
                )
            
            return False, False
        
        close_long_position, close_short_position = False, False
        
        if event_signal == SignalType.EXIT:
            close_long_position = trade_state_signal == SignalType.BUY or self.insufficient_equity
            close_short_position = trade_state_signal == SignalType.SELL or self.insufficient_equity
        else:
            close_long_position, close_short_position = {
                SignalType.BUY: should_close_buy_position,
                SignalType.SELL: should_close_sell_position
            }[event_signal]()
            
        return close_long_position, close_short_position
from backtestify.signal_type import SignalType
from backtestify.trade import Trade

class TradeExecutor:
    def __init__(self, timestamp, current_bar, equity, margin, currency_ratio):
        self.timestamp = timestamp
        self.current_bar = current_bar
        self.equity = equity
        self.margin = margin
        self.currency_ratio = currency_ratio
        self.insufficient_equity = self.equity <= self.margin * self.currency_ratio
        self.open_price = None
        self.high_price = None
        self.low_price = None
        self.close_price = None
        self.trade_state_price = None

    def open_trade(
        self, 
        trade_state, 
        commission, 
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
        trade_state.balance -= commission
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
            if self.insufficient_equity:
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
            if self.insufficient_equity:
                return False, True
            
            if trade_state_signal == SignalType.SELL:
                return (
                    (use_stop_loss and stop_loss <= (open_price + spread_points)) or
                    (use_take_profit and take_profit >= (open_price + spread_points))
                )
            
            return False, False
        
        close_buy_position, close_sell_position = False, False
        
        if event_signal == SignalType.EXIT:
            close_buy_position = trade_state_signal == SignalType.BUY or self.insufficient_equity
            close_sell_position = trade_state_signal == SignalType.SELL or self.insufficient_equity
        else:
            close_buy_position = should_close_buy_position()
            close_sell_position = should_close_sell_position()
                    
        return close_buy_position, close_sell_position
    
    def close_trade(
        self,
        trade_state,
        trade_state_signal,
        open_price,
        spread_point,
        position_size,
        trade_state_price,
        event_signal
    ):
        profit = self.calculate_profit(
            trade_state_signal,
            open_price,
            position_size,
            trade_state_price,
            spread_point
        )

        trade_state.signal = event_signal
        trade_state.size = 0
        trade_state.unrealized_profit = 0
        trade_state.realized_profit = profit
        trade_state.balance += profit
        trade_state.equity = trade_state.balance
        
        trade = Trade(
            timestamp=self.timestamp,
            bar=self.current_bar,
            signal=event_signal,
            size=position_size * (1 if event_signal == SignalType.BUY else -1),
            price=trade_state.adjusted_price,
            profit=profit,
            balance=trade_state.balance,
            stop_loss=trade_state.stop_loss,
            take_profit=trade_state.take_profit
        )

        return trade


    def calculate_profit(
        self, 
        trade_state_signal, 
        open_price, 
        position_size, 
        trade_state_price,
        spread_point
    ):
        profit = 0
        
        if trade_state_signal == SignalType.BUY:
            profit = self.calculate_buy_profit(position_size, open_price, trade_state_price)
        elif trade_state_signal == SignalType.SELL:
            profit = self.calculate_sell_profit(open_price, spread_point, position_size, trade_state_price)

        return profit

    def calculate_buy_profit(self, position_size, open_price, trade_state_price):
        profit = position_size * (open_price - trade_state_price)
        return profit
    
    def calculate_sell_profit(self, open_price, spread_point, position_size, trade_state_price):
        adjusted_close_price = open_price + spread_point
        profit = position_size * (trade_state_price - adjusted_close_price)
        return profit
    
    def execute_stop_loss(self, is_trade_open, trade_state, trade_state_signal, open_price, low_price, high_price, close_price, spread_points, previous_close_price, commission, position_size, point_value, event_signal):        
        profit = 0
        
        if trade_state_signal == SignalType.BUY and low_price <= trade_state.stop_loss:
            if (trade_state_signal == SignalType.BUY) and (not is_trade_open and previous_close_price > trade_state.stop_loss and open_price < trade_state.stop_loss):
                trade_state.stop_loss = open_price

            profit = (
                position_size
                * (trade_state.stop_loss - trade_state.adjusted_price)
                * point_value
                * self.currency_ratio
                - commission
            )

        if trade_state_signal == SignalType.SELL and high_price + spread_points >= trade_state.stop_loss:
            if (trade_state_signal == SignalType.SELL) and (not is_trade_open and close_price < trade_state.stop_loss and trade_state.stop_loss <= self.open_price + spread_points):
                trade_state.stop_loss = open_price + spread_points
            
            profit = (
                position_size
                * (trade_state.adjusted_price - trade_state.stop_loss)
                * point_value
                * self.currency_ratio
                - commission
            )

        trade_state.signal = None
        trade_state.size = 0
        trade_state.unrealized_profit = 0
        trade_state.realized_profit = profit
        trade_state.balance += profit
        trade_state.equity = trade_state.balance

        trade = Trade(
            timestamp=self.timestamp,
            bar=self.current_bar,
            signal=SignalType.STOP_LOSS,
            size=position_size * (1 if event_signal == SignalType.BUY else -1),
            price=trade_state.stop_loss,
            profit=profit,
            balance=trade_state.balance,
            stop_loss=trade_state.stop_loss,
            take_profit=trade_state.take_profit
        )

        return trade

    def execute_take_profit(self, is_trade_open, trade_state, trade_state_signal, open_price, low_price, high_price, close_price, spread_points, previous_close_price, commission, position_size, point_value, event_signal):
        profit = 0
        
        if trade_state_signal == SignalType.BUY:
            if not is_trade_open and self.open_price >= trade_state.take_profit:
                trade_state.take_profit = self.open_price

            if high_price >= trade_state.take_profit:
                profit = (
                            self.instrument.position_size
                            * (trade_state.take_profit - trade_state.adjusted_price)
                            * self.instrument.point_value
                            * self.instrument.currency_ratio
                            - commission
                        )
                
        if trade_state.signal == SignalType.SELL:
            if (
                not is_trade_open and
                close_price > trade_state.take_profit and
                trade_state.take_profit >= self.open_price + spread_points
            ):
                trade_state.take_profit = self.open_price + spread_points

            if low_price <= trade_state.take_profit:
                profit = (
                    self.instrument.position_size
                    * (trade_state.adjusted_price - trade_state.take_profit)
                    * self.instrument.point_value
                    * self.instrument.currency_ratio
                    - commission
                )

        trade_state.signal = None
        trade_state.size = 0
        trade_state.unrealized_profit = 0
        trade_state.realized_profit = profit
        trade_state.balance += profit
        trade_state.equity = trade_state.balance

        trade = Trade(
            timestamp=self.timestamp,
            bar=self.current_bar,
            signal=SignalType.TAKE_PROFIT,
            size=position_size * (1 if event_signal == SignalType.BUY else -1),
            price=trade_state.take_profit,
            profit=profit,
            balance=trade_state.balance,
            stop_loss=trade_state.stop_loss,
            take_profit=trade_state.take_profit
        )

        return trade
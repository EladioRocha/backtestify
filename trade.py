class Trade:
    def __init__(
        self,
        timestamp,
        bar,
        signal,
        size,
        price,
        profit,
        balance,
        stop_loss,
        take_profit
    ):
        self.timestamp = timestamp
        self.bar = bar
        self.signal = signal
        self.size = size
        self.price = price
        self.profit = profit
        self.balance = balance
        self.stop_loss = stop_loss
        self.take_profit = take_profit
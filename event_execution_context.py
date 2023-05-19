class EventExecutionContext:
    def __init__(self, instrument=None, balance=None, current_trade_state=None, current_bar=None):
        self.instrument = instrument
        self.balance = balance
        self.current_trade_state = current_trade_state
        self.current_bar = current_bar

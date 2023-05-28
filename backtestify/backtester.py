from backtestify.trade_state import TradeState
from backtestify.event_execution_context import EventExecutionContext
from backtestify.event_execution_strategy import SignalEventExecutionStrategy
from backtestify.signal_event import SignalEvent
from backtestify.trade import Trade

class Backtester:
    def __init__(self, strategy, instrument, account):
        self.strategy = strategy
        self.instrument = instrument
        self.account = account
        self.events = []
        self.trading_state = []
        self.trades = []
        self.current_trade_state = None

    def run(self):
        events = self.strategy.generate_signals()
        print(f'Generated {len(events)} events')
        self.events.extend(events)
        self.execute()

    def execute(self):
        self.trading_state = [None] * len(self.events)

        for current_bar, event in enumerate(self.events):
            execution_strategy = self.get_execution_strategy(event)
            context = EventExecutionContext(
                instrument=self.instrument, 
                balance=self.account.balance, 
                current_trade_state=self.current_trade_state, 
                current_bar=current_bar
            )

            response = execution_strategy.execute(event, context)

            self.handle_execution_response(response, current_bar, execution_strategy)

    def get_execution_strategy(self, event):
        if isinstance(event, SignalEvent):
            return SignalEventExecutionStrategy()
        else:
            raise NotImplementedError("Unknown event type")

    def handle_execution_response(self, response, current_bar, execution_strategy):
        if isinstance(execution_strategy, SignalEventExecutionStrategy):
            self.handle_signal_event_execution_response(response, current_bar)
        else:
            raise NotImplementedError("Unknown execution strategy")
        
    def handle_signal_event_execution_response(self, response, current_bar):
        if response is None:
            return

        # If is not a list or tuple, convert it to a list
        if not isinstance(response, (list, tuple)):
            response = [response]

        for res in response:
            if isinstance(res, TradeState):
                self.trading_state[current_bar] = res
                self.current_trade_state = res
            elif isinstance(res, Trade):
                self.trades.append(res)



class EventExecutionStrategy:
    def execute(self, event, context):
        raise NotImplementedError("execute() method must be implemented by subclass.")
    
class SignalEventExecutionStrategy(EventExecutionStrategy):
    def execute(self, event, context):
        return event.execute(
            instrument=context.instrument, 
            balance=context.balance, 
            current_trade_state=context.current_trade_state,
            current_bar=context.current_bar,
        )
from backtestify.event_type import EventType
from backtestify.event import Event
from backtestify.signal_event import SignalEvent
from backtestify.signal_type import SignalType

class Strategy:
    def __init__(self, prices_info):
        self.prices_info = prices_info
        self.current_index = 0
        self.events = []

    def get_past_info(self, shift=1):
        return self.prices_info.iloc[:self.current_index + shift]
    
    def set_ohlcv(self, signal):
        required_columns = ["open", "high", "low", "close"]
        optional_columns = ["volume"]

        past_info = self.get_past_info()

        for column in required_columns:
            if column not in past_info.columns:
                raise ValueError(f"The market info must have a '{column}' column.")
            setattr(signal, f"{column}_price", past_info[column].iloc[-1])

        for column in optional_columns:
            if column in past_info.columns:
                setattr(signal, column, past_info[column].iloc[-1])

    def set_timestamp_if_none(self, signal):
        if signal.timestamp is not None:
            return None

        past_info = self.get_past_info()

        if past_info.index.name == "timestamp":
            signal.timestamp = past_info.index[-1]
        elif "timestamp" in past_info.columns:
            signal.timestamp = past_info["timestamp"].iloc[-1]
        else:
            raise ValueError("The market info must have a 'timestam' column or index.")

        return None
        
    def set_swap_info_if_none(self, signal):
        past_info = self.get_past_info()

        if signal.swap_long is not None and signal.swap_short is not None:
            return None

        past_info = self.get_past_info()

        for attr in ["swap_long", "swap_short"]:
            last_value = past_info.get(attr)
            setattr(signal, attr, last_value.iloc[-1] if last_value is not None else 0)

    def set_symbol_if_none(self, signal):
        past_info = self.get_past_info()

        if signal.symbol is not None or "symbol" not in past_info.columns:
            return
        
        signal.symbol = past_info["symbol"].iloc[-1]

    def get_signal_events(self, events):
        return [event for event in events if event.event_type == EventType.SIGNAL]

    def get_signal_event(self, events):
        signal_events = self.get_signal_events(events)

        if len(signal_events) == 0:
            return None
        
        return signal_events[0]

    def set_previous_event(self, signal):
        if len(self.events) == 0:
            signal.previous_event = None
            return None

        signal.previous_event = self.events[-1]

    def set_bar_index(self, signal):
        signal.bar = self.current_index + 1

    def set_information(self, signals):
        signals = self.get_signal_events(signals)

        for signal in signals:
            self.set_ohlcv(signal)
            self.set_timestamp_if_none(signal)
            self.set_swap_info_if_none(signal)
            self.set_symbol_if_none(signal)
            self.set_previous_event(signal)
            self.set_bar_index(signal)

    def apply_strategy(self, next_candle):
        # Save the amount of size of the prices_info
        prices_info_size = len(self.prices_info)

        for index, _ in enumerate(self.prices_info.itertuples()):
            self.current_index = index
            history = self.get_past_info(shift=1)
            result_events = next_candle(history)

            # Create initial event to open the first trade
            initial_event = SignalEvent(signal=None) if index == 0 else None

            # Create last event to close the last trade
            last_event = SignalEvent(signal=SignalType.EXIT) if index == prices_info_size - 1 else None

            if result_events is None or (isinstance(result_events, (list, tuple)) and not result_events):
                result_events = [SignalEvent(signal=None)]
            elif isinstance(result_events, Event):
                result_events = [result_events]

            if initial_event:
                # The initial event is always none because is the way to create the trade state
                result_events = [initial_event, *result_events]
            if last_event:
                result_events.append(last_event)

            self.set_information(result_events)
            self.events.extend(result_events)

        return self.events

    def generate_signals(self):
        if not hasattr(self, "next_candle"):
            raise NotImplementedError("Subclasses should implement a next_candle method.")
        
        events = self.apply_strategy(self.next_candle)
        return events
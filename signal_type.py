from enum import Enum, auto

class SignalType(Enum):
    BUY = auto()
    SELL = auto()
    EXIT = auto()
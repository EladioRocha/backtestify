class FinancialInstrument:
    def __init__(self, symbol, lot_size, entry_lots, commission, leverage, period, currency_ratio=1):
        self.symbol = symbol
        self.lot_size = lot_size
        self.entry_lots = entry_lots
        self.commission = commission
        self.leverage = leverage
        self.position_size = entry_lots * lot_size
        self.period = period
        self.currency_ratio = currency_ratio
from financial_instrument import FinancialInstrument

class CFD(FinancialInstrument):
    def __init__(self, symbol, instrument_type, lot_size, entry_lots, commission, point_value, leverage, period, point, spread, pips, currency_ratio=1):
        super().__init__(symbol, lot_size, entry_lots, commission, leverage, period, currency_ratio)
        self.instrument_type = instrument_type
        self.pips = pips
        self.point_value = point_value
        self.point = point
        self.spread = spread
        self.spread_points = spread * point
        self.margin = self.position_size / leverage
        self.required_margin = self.margin * self.currency_ratio
class Account:
    def __init__(self, initial_balance):
        self.balance = initial_balance
        self.equity = self.balance
        
    def set_balance(self, balance):
        self.balance = balance

    def set_equity(self, equity):
        self.equity = equity
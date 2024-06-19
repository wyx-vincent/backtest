class Portfolio:
    def __init__(self, initial_cash):
        self.cash = initial_cash
        self.shares = int(initial_cash/1)      # assume $1 per share
        self.port_value_history = [initial_cash]
        self.nav_history = [initial_cash/self.shares]
        self.positions = {}
        self.liability = 0
        self.dates = []
        self.transaction_history = {}

    def record_date(self, dates):
        self.dates = dates
        self.transaction_history = {date: [] for date in dates}

    def buy(self, date, asset, price, quantity, leverage=1):
        buying_power = self.cash * leverage
        cost = price * quantity / leverage
        if cost <= buying_power:
            if asset not in self.positions:
                self.positions[asset] = 0
            self.positions[asset] += quantity
            self.cash -= cost
            self.transaction_history[date].append(f"bought {quantity} {asset} at {price} on {date}.")
        else:
            error = (f"Not enough buying power to buy {quantity} {asset} at {price} on {date}. "
                     f"Available cash: {self.cash}, Required: {cost}, Leverage: {leverage}")
            raise Exception(error)
        
    def sell(self, date, asset, price, quantity):
        if asset in self.positions and self.positions[asset] >= quantity:
            self.positions[asset] -= quantity
            self.cash += price * quantity
            self.transaction_history[date].append(f"sold {quantity} {asset} at {price} on {date}.")
        else:
            error = (f"Not enough {asset} to sell {quantity} on {date}. "
                     f"Current position: {self.positions.get(asset, 0)}")
            raise Exception(error)

    def short(self, date, asset, price, quantity):
        proceeds = price * quantity
        if asset not in self.positions:
            self.positions[asset] = 0
        self.positions[asset] -= quantity
        self.cash += proceeds
        self.liability += proceeds
        self.transaction_history[date].append(f"shorted {quantity} {asset} at {price} on {date}.")

    def cover_short(self, date, asset, price, quantity):
        pass

    def update_liability(self):
        pass

    def update_port_value(self):
        pass

from utils import AssetClassValidator as ACV

class Portfolio:
    def __init__(self, initial_cash, portfolio_weights_config):
        self.asset_cash = {}
        self.portfolio_weights = portfolio_weights_config

        total_weight = sum(self.portfolio_weights.values())
        if total_weight != 1:
            raise ValueError(f"Total portfolio weights must sum to 1, but the sum is {total_weight}")
        
        for asset_class, weight in self.portfolio_weights.items():
            ACV.is_valid_asset_class(asset_class)
            self.asset_cash[asset_class] = initial_cash * weight
        
        self.shares = initial_cash              # assume $1 per share
        self.port_value_history = [initial_cash]
        self.nav_history = [initial_cash/self.shares]
        self.positions = {}                     # positions can be negative
        self.cash_liability = 0
        self.dates = None
        self.transaction_history = {}


    @property
    def total_cash(self):
        return sum(self.asset_cash.values())


    def record_date(self, dates):
        # todo: check dates format
        if self.dates is None:
            self.dates = dates
            self.transaction_history = {date: [] for date in dates}
        else:
            raise Exception("record_date method has already been run.")


    def check_date(self, date):
        if self.dates is None:
            raise Exception("dates have not been recorded by record_date function")
        if date not in self.dates:
            raise ValueError(f"The given date {date} does not exist in the backtest period")
        
    
    @staticmethod
    def check_positive_quantity(quantity):
        if quantity <= 0:
            raise ValueError('The quantity must be positive')


    def update_positions(self, asset, quantity_change):
        if asset not in self.positions:
            self.positions[asset] = 0
        self.positions[asset] += quantity_change


    @ACV.validate_asset_class
    def enough_cash(self, asset_class, cash_needed):
        return self.asset_cash[asset_class] >= cash_needed
    

    def enough_quantity(self, asset, quantity_needed):
        return asset in self.positions and self.positions[asset] >= quantity_needed


    @ACV.validate_asset_class
    def buy(self, date, asset, asset_class, price, quantity, leverage=1):
        self.check_date(date)
        Portfolio.check_positive_quantity(quantity)
        notional_cost = price * quantity
        cash_needed = notional_cost / leverage
        cash_borrowed  = notional_cost - cash_needed
        if self.enough_cash(asset_class, cash_needed):
            self.asset_cash[asset_class] -= cash_needed
            self.update_positions(asset, quantity_change=quantity)
            if cash_borrowed > 0:
                self.cash_liability += cash_borrowed
            self.transaction_history[date].append(f"bought {quantity} {asset} at {price} on {date}.")
        else:
            error = (f"Not enough buying power to buy {quantity} {asset} at {price} on {date}. "
                     f"Available cash: {self.asset_cash[asset_class]}, Required: {cash_needed}, Leverage: {leverage}")
            raise Exception(error)


    @ACV.validate_asset_class
    def sell(self, date, asset, asset_class, price, quantity):
        self.check_date(date)
        Portfolio.check_positive_quantity(quantity)
        if self.enough_quantity(asset, quantity):
            proceeds = price * quantity
            self.asset_cash[asset_class] += proceeds
            self.update_positions(asset, quantity_change=-quantity)
            self.transaction_history[date].append(f"sold {quantity} {asset} at {price} on {date}, remaining quantity: {self.positions[asset]}")
        else:
            error = (f"Not enough {asset} to sell at {price} on {date}. "
                     f"Available: {self.positions.get(asset, 0)}, Intend to sell: {quantity}")
            raise Exception(error)


    # unfinished
    def short(self, date, asset, price, quantity, leverage=1):
        proceeds = price * quantity
        if asset not in self.positions:
            self.positions[asset] = 0
        self.positions[asset] -= quantity
        self.cash += proceeds
        self.liability += proceeds
        self.transaction_history[date].append(f"shorted {quantity} {asset} at {price} on {date}.")

    def cover_short(self, date, asset, price, quantity):
        pass


    def get_port_value(self, asset_price_dict):
        total_value = self.total_cash - self.cash_liability

        # Add value of positions
        for asset, quantity in self.positions.items():
            if quantity == 0:
                continue
            if asset in asset_price_dict:
                total_value += asset_price_dict[asset] * quantity
            else:
                raise Exception(f"Asset {asset} in positions is not in asset_price_dict")

        return total_value

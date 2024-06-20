from utils import AssetClassValidator as ACV

class Portfolio:
    def __init__(self, initial_cash, portfolio_weights_config):

        total_weight = sum(portfolio_weights_config.values())
        if total_weight != 1:
            raise ValueError(f"Total portfolio weights must sum to 1, but the sum is {total_weight}")
        
        for asset_class in portfolio_weights_config:
            ACV.is_valid_asset_class(asset_class)

        self._cash = initial_cash
        self._cash_liability = 0
        self._positions = {}
        self.target_portfolio_weights = portfolio_weights_config
        self.shares = initial_cash              # assume $1 per share
        self.port_value_history = [initial_cash]
        self.nav_history = [initial_cash/self.shares]
        self.transaction_history = {}
        self.dates = None
        

    @property
    def cash(self):
        return self._cash
    
    @property
    def cash_liability(self):
        return self._cash_liability

    @property
    def positions(self):
        # Create a new dictionary that only includes items (assets) with non-zero values (positions)

        # Remove entries where the value is 0 at the asset level
        filtered_positions = {asset_class: {asset: value for asset, value in assets.items() if value != 0}
                              for asset_class, assets in self._positions.items()}
        # Remove any asset classes that are now empty
        filtered_positions = {asset_class: assets for asset_class, assets in filtered_positions.items() if assets}
    
        return filtered_positions


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


    @ACV.validate_asset_class
    def has_asset_class(self, asset_class):
        return asset_class in self._positions 
    

    @ACV.validate_asset_class
    def has_asset(self, asset_class, asset):
        return asset in self._positions[asset_class]
    

    @ACV.validate_asset_class
    def update_positions(self, asset_class, asset, quantity_change):
        if not self.has_asset_class(asset_class):
            self._positions[asset_class] = {}
        if not self.has_asset(asset_class, asset):
            self._positions[asset_class][asset] = 0
        self._positions[asset_class][asset] += quantity_change


    @ACV.validate_asset_class
    def enough_quantity(self, asset_class, asset, quantity_to_sell=None, quantity_to_cover_short=None):
        cond1 = self.has_asset_class(asset_class)
        cond2 = self.has_asset(asset_class, asset)
        if quantity_to_sell is None and quantity_to_cover_short is None:
            raise Exception('Order quantity must be defined')
        if quantity_to_sell is not None:     # sell
            cond3 = self._positions[asset_class][asset] >= quantity_to_sell
        if quantity_to_cover_short is not None:     # cover short
            neg_quantity = -quantity_to_cover_short
            cond3 = self._positions[asset_class][asset] <= neg_quantity

        return cond1 and cond2 and cond3


    @ACV.validate_asset_class
    def buy(self, date, asset_class, asset, price, quantity, leverage=1):
        self.check_date(date)
        Portfolio.check_positive_quantity(quantity)
        notional_cost = price * quantity
        cash_needed = notional_cost / leverage
        cash_borrowed  = notional_cost - cash_needed
        if self._cash > cash_needed:
            self._cash -= cash_needed
            self.update_positions(asset_class, asset, quantity_change=quantity)
            if cash_borrowed > 0:
                self._cash_liability += cash_borrowed
            self.transaction_history[date].append(f"bought {quantity} {asset} at {price} on {date}.")
        else:
            error = (f"Not enough buying power to buy {quantity} {asset} at {price} on {date}. "
                     f"Available cash: {self._cash}, Required: {cash_needed}, Leverage: {leverage}")
            raise Exception(error)


    @ACV.validate_asset_class
    def sell(self, date, asset_class, asset, price, quantity):
        self.check_date(date)
        Portfolio.check_positive_quantity(quantity)
        if self.enough_quantity(asset_class, asset, quantity_to_sell=quantity):
            proceeds = price * quantity
            self._cash += proceeds
            self.update_positions(asset_class, asset, quantity_change=-quantity)
            self.transaction_history[date].append(f"sold {quantity} {asset} at {price} on {date}, remaining quantity: {self._positions[asset_class][asset]}")
        else:
            error = (f"Not enough {asset} to sell at {price} on {date}. "
                     f"Available: {self._positions[asset_class].get(asset, 0)}, Intend to sell: {quantity}")
            raise Exception(error)


    @ACV.validate_asset_class
    def short(self, date, asset_class, asset, price, quantity, leverage=1):
        self.check_date(date)
        Portfolio.check_positive_quantity(quantity)
        notional_proceed = price * quantity
        margin = notional_proceed / leverage

        if self._cash > margin:
            self._cash -= margin
            self._cash += notional_proceed
            self.update_positions(asset_class, asset, quantity_change=-quantity)
            self.transaction_history[date].append(f"shorted {quantity} {asset} at {price} on {date}.")
        else:
            error = (f"Not enough shorting power to short {quantity} {asset} at {price} on {date}. "
                     f"Available cash: {self._cash}, Required magin: {margin}, Leverage: {leverage}")
            raise Exception(error)
        

    @ACV.validate_asset_class
    def cover_short(self, date, asset_class, asset, price, quantity):
        """
        After short selling, the quantity in portfolio.positions is negative.
        use positive quantity in this function to cover previous short positions.
        """
        self.check_date(date)
        Portfolio.check_positive_quantity(quantity)
        if self.enough_quantity(asset_class, asset, quantity_to_cover_short=quantity):
            self.buy(date, asset_class, asset, price, quantity)
        else:
            error = (f"The order quantity is larger than the short position in {asset}. "
                     f"Short position: {self._positions[asset_class].get(asset, 0)}, Intend to cover: {quantity}")
            raise Exception(error)
        

    def get_port_value(self, asset_price_dict):
        total_value = self._cash - self._cash_liability

        for asset_class in asset_price_dict:
            ACV.is_valid_asset_class(asset_class)

            for asset, quantity in self._positions[asset_class].items():
                if quantity == 0:
                    continue
                if asset in asset_price_dict[asset_class]:
                    total_value += asset_price_dict[asset_class][asset] * quantity
                else:
                    raise Exception(f"Asset {asset} in positions is not in asset_price_dict")

        return total_value
    

    def check_weights():
        pass


    def print_transaction_history(self):
        for date, transactions in self.transaction_history.items():
            if transactions:
                print(f'{date}: {transactions}')

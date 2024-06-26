import os

import pandas as pd

from utils import AssetClassValidator as ACV



class Portfolio:
    def __init__(self, initial_portfolio_nominal_value, portfolio_weights_config, collateral_ratio=1):

        total_weight = sum(portfolio_weights_config.values())
        if total_weight != collateral_ratio:
            raise ValueError(f"Total portfolio weights must sum to collateral_ratio, but the sum is {total_weight}")
        for asset_class in portfolio_weights_config:
            if portfolio_weights_config[asset_class] > 1 and asset_class != 'cash':
                raise ValueError(f"The initial weight of {asset_class} cannot be larger than 1. ")

        for asset_class in portfolio_weights_config:
            ACV.is_valid_asset_class(asset_class)

        self.initial_portfolio_nominal_value = initial_portfolio_nominal_value
        self._cash = initial_portfolio_nominal_value * collateral_ratio
        self._cash_liability = 0
        self._positions = {}
        self._margin = {}
        self.collateral_ratio = collateral_ratio
        self.target_portfolio_weights = portfolio_weights_config
        self.shares = initial_portfolio_nominal_value                       # investor paying $collateral_ratio per share to invest in this fund
        self.port_value_history = [initial_portfolio_nominal_value * collateral_ratio]   # real portfolio value (including overcollateralization)
        self.nav_history = [initial_portfolio_nominal_value / self.shares]      # nav=1 at init
        self.equity_exposure = [portfolio_weights_config['equity']]
        self.cash_exposure = [portfolio_weights_config['cash']]
        self.transaction_history = {}
        self.dates = None
        

    @property
    def cash(self):
        return round(self._cash, 2)
    
    @property
    def cash_liability(self):
        return round(self._cash_liability, 2)

    @property
    def positions(self):
        # Create a new dictionary that only includes items (assets) with non-zero values (positions)

        # Remove entries where the value is 0 at the asset level
        filtered_positions = {asset_class: {asset: value for asset, value in assets.items() if value != 0}
                              for asset_class, assets in self._positions.items()}
        # Remove any asset classes that are now empty
        filtered_positions = {asset_class: assets for asset_class, assets in filtered_positions.items() if assets}
    
        return filtered_positions

    @property
    def margin(self):
        return self._margin


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
    def has_asset_class(self, asset_class, attribute):
        return asset_class in getattr(self, f'{attribute}')
    

    @ACV.validate_asset_class
    def has_asset(self, asset_class, asset, attribute):
        attribute_data = getattr(self, f'{attribute}')
        return asset in attribute_data.get(asset_class, ())
    

    def update_margin_account(self, asset_class, asset, margin_balance_change):
        if not self.has_asset_class(asset_class, '_margin'):
            self._margin[asset_class] = {}
        if not self.has_asset(asset_class, asset, '_margin'):
            self._margin[asset_class][asset] = 0
        self._margin[asset_class][asset] += margin_balance_change
        

    @ACV.validate_asset_class
    def has_margin_account(self, asset_class, asset):
        cond1 = self.has_asset_class(asset_class, '_margin')
        cond2 = self.has_asset(asset_class, asset, '_margin')
        cond3 = self._margin[asset_class][asset] != 0

        return cond1 and cond2 and cond3
    

    @ACV.validate_asset_class
    def update_positions(self, asset_class, asset, quantity_change):
        if not self.has_asset_class(asset_class, attribute='_positions'):
            self._positions[asset_class] = {}
        if not self.has_asset(asset_class, asset, attribute='_positions'):
            self._positions[asset_class][asset] = 0
        self._positions[asset_class][asset] += quantity_change


    @ACV.validate_asset_class
    def enough_quantity(self, asset_class, asset, quantity_to_sell=None, quantity_to_cover_short=None):
        cond1 = self.has_asset_class(asset_class, attribute='_positions')
        cond2 = self.has_asset(asset_class, asset, attribute='_positions')
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
        if self._cash >= cash_needed:
            self._cash -= cash_needed
            self.update_positions(asset_class, asset, quantity_change=quantity)
            if cash_borrowed > 0:
                self._cash_liability += cash_borrowed
            self.transaction_history[date].append(f"bought {quantity} {asset} at {round(price, 4)} on {date}.")
        else:
            error = (f"Not enough buying power to buy {quantity} {asset} at {round(price, 4)} on {date}. "
                     f"Available cash: {self.cash}, Required: {round(cash_needed, 2)}, Leverage: {leverage}")
            raise Exception(error)


    @ACV.validate_asset_class
    def sell(self, date, asset_class, asset, price, quantity):
        self.check_date(date)
        Portfolio.check_positive_quantity(quantity)
        if self.enough_quantity(asset_class, asset, quantity_to_sell=quantity):
            proceeds = price * quantity
            self._cash += proceeds
            self.update_positions(asset_class, asset, quantity_change=-quantity)
            self.transaction_history[date].append(f"sold {quantity} {asset} at {round(price, 4)} on {date}, remaining quantity: {self._positions[asset_class][asset]}")
        else:
            error = (f"Not enough {asset} to sell at {round(price, 4)} on {date}. "
                     f"Available: {self._positions[asset_class].get(asset, 0)}, Intend to sell: {quantity}")
            raise Exception(error)


    @ACV.validate_asset_class
    def short(self, date, asset_class, asset, price, quantity, leverage=1):
        self.check_date(date)
        Portfolio.check_positive_quantity(quantity)
        proceed = price * quantity
        required_margin = proceed / leverage
        available_to_cash= proceed - required_margin
        if self._cash >= required_margin:
            self._cash += available_to_cash
            self.update_margin_account(asset_class, asset, required_margin)
            self.update_positions(asset_class, asset, quantity_change=-quantity)
            self.transaction_history[date].append(f"shorted {quantity} {asset} at {round(price, 4)} on {date}.")
        else:
            error = (f"Not enough cash to short {quantity} {asset} at {round(price, 4)} on {date}. "
                     f"Available cash: {self.cash}, Required magin: {round(required_margin, 2)}, Leverage: {leverage}")
            raise Exception(error)
        

    @ACV.validate_asset_class
    def cover_short(self, date, asset_class, asset, price, quantity):
        """
        After short selling, the quantity in portfolio.positions is negative.
        use positive quantity in this function to cover previous short positions.
        """
        self.check_date(date)
        Portfolio.check_positive_quantity(quantity)

        if not self.has_margin_account(asset_class, asset):
            error1 = f"No margin account for {asset}. "
            raise Exception(error1)
        
        if not self.enough_quantity(asset_class, asset, quantity_to_cover_short=quantity):
            error2 = (f"The order quantity is larger than the short position in {asset}. "
                    f"Short position: {self._positions[asset_class].get(asset, 0)}, Intend to cover: {quantity}")
            raise Exception(error2)
        
        cover_ratio = quantity / -self._positions[asset_class][asset]   # asset position should be negative
        cash_required_to_cover = price * quantity - self._margin[asset_class][asset] * cover_ratio
        if self._cash < cash_required_to_cover:
            error3 = (f"Trying to cover short position in {asset} on {date}, but cash is not enough. "
                        f"Total cash needed: {round(price * quantity, 2)}, margin account balance: {round(self._margin[asset_class][asset], 2)}, cash balance: {self.cash}")
            raise Exception(error3)

        # it's ok to release fund from margin account to cash account before calling 'buy' function, as we have checked we have enough cash above
        cash_released = self._margin[asset_class][asset] * cover_ratio
        self._cash += cash_released
        self.update_margin_account(asset_class, asset, -cash_released)
        self.buy(date, asset_class, asset, price, quantity)
        # delete the key and value in self._margin[asset_class] dictionary if the margin_balance is reduced to 0
        if not self.has_margin_account(asset_class, asset):
            del self._margin[asset_class][asset]


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
    

    def record_port_value(self, asset_price_dict):
        value = self.get_port_value(asset_price_dict)
        self.port_value_history.append(value)


    def record_nav(self):
        value = self.port_value_history[-1] / self.collateral_ratio / self.shares
        self.nav_history.append(value)


    def record_equity_exposure(self, asset_price_dict, asset):

        if not self.has_asset_class('equity', attribute='_positions'):
            raise Exception("There is no equity in portfolio")
        elif not self.has_asset('equity', asset, attribute='_positions'):
            raise Exception("There is no {asset} in portfolio")
        elif 'equity' not in asset_price_dict:
            raise Exception("There is no equity in the asset_price_dict")
        elif asset not in asset_price_dict['equity']:
            raise Exception("There is no {asset} in the asset_price_dict")
        else:
            quantity = self.positions['equity'][asset]
            price = asset_price_dict['equity'][asset]
            value = quantity * price / self.initial_portfolio_nominal_value
            self.equity_exposure.append(value)


    def record_cash_exposure(self):
        self.cash_exposure.append(self._cash / self.initial_portfolio_nominal_value)


    def check_weights():
        pass


    def rebalance():
        pass


    def print_transaction_history(self):
        for date, transactions in self.transaction_history.items():
            if transactions:
                print(f'{date}: {transactions}')


    def calc_port_daily_return(self):
        value_series = pd.Series(self.port_value_history)
        return_series = value_series.pct_change().dropna()

        return return_series


    def update(self, price_dict, equity):
        self.record_port_value(price_dict)
        self.record_nav()
        self.record_equity_exposure(price_dict, equity)
        self.record_cash_exposure()


    def save_transaction_history_to_csv(self, filename='portfolio_transaction_history.csv'):

        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, 'data', filename)

        tx_df = pd.DataFrame(list(self.transaction_history.items()), columns=['Date', 'Transactions'])
        temp_df = pd.DataFrame(tx_df['Transactions'].tolist()).add_prefix('Transaction ')
        tx_df = pd.concat([tx_df['Date'], temp_df], axis=1)
        tx_df.to_csv(file_path)
import pandas as pd

from portfolio import Portfolio
from .strategy import Strategy
from utils.asset_class_validator import AssetClassValidator as ACV

class BuyAndHold(Strategy):
    @ACV.validate_asset_class
    def __init__(self, asset: str, asset_class: str, underlying_data: pd.DataFrame, option_data: pd.DataFrame = None):
        super().__init__(underlying_data, option_data)
        self.asset = asset
        self.asset_class = asset_class
        self.bought = False
    
    def execute(self, portfolio: Portfolio, execution_date: str, execution_price: float, quantity: float, leverage: float=1):
        if not isinstance(portfolio, Portfolio):
            raise ValueError("portfolio must be an instance of Portfolio")
        
        if not self.bought:
            portfolio.buy(execution_date, self.asset, self.asset_class, execution_price, quantity, leverage)
            self.bought = True


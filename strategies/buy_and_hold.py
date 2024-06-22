import pandas as pd

from portfolio import Portfolio
from .strategy import Strategy
from utils.asset_class_validator import AssetClassValidator as ACV

class BuyAndHold(Strategy):
    @ACV.validate_asset_class
    def __init__(self, portfolio: Portfolio, asset_class: str, asset: str, asset_data: pd.DataFrame):
        super().__init__(portfolio, asset, asset_data)
        self.asset_class = asset_class
        self.bought = False

    
    def execute(self, execution_date: str, execution_price: float, quantity: float, leverage: float=1):
        if not self.bought:
            self.portfolio.buy(execution_date, self.asset_class, self.asset, execution_price, quantity, leverage)
            self.bought = True 
        else:
            raise Exception('The asset was bought before, BuyAndHold strategy is used to buy asset only once')


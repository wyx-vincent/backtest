import pandas as pd

from portfolio import Portfolio
from .strategy import Strategy

class BuyAndHold(Strategy):
    def __init__(self, asset: str, underlying_data: pd.DataFrame, option_data: pd.DataFrame = None):
        super().__init__(underlying_data, option_data)
        self.asset = asset
        self.bought = False
    
    def execute(self, portfolio: Portfolio, execution_date: str, execution_price: float, quantity: float, leverage: float=1):
        if not isinstance(portfolio, Portfolio):
            raise ValueError("portfolio must be an instance of Portfolio")
        
        if not self.bought:
            portfolio.buy(execution_date, self.asset, execution_price, quantity, leverage)
            self.bought = True


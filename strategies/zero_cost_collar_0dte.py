import pandas as pd

from .strategy import Strategy
from .buy_and_hold import BuyAndHold
from utils.asset_class_validator import AssetClassValidator as ACV

class ZeroCostCollar0DTE(Strategy):
    def __init__(self, portfolio, underlying_asset: str, asset_data: pd.DataFrame, option_data: pd.DataFrame):
        super().__init__(portfolio, underlying_asset, asset_data)
        self.underlying_asset = underlying_asset
        self.option_data = option_data


    def update_collar_pnl(self, backtest_main_df: pd.DataFrame):
        """
        Only calculates pnl of the option positions (i.e. excluding pnl from holding underlying asset)
        """
        result_df = backtest_main_df.copy()
        result_df['collar_cost'] = result_df['put_price_at_open'] - result_df['call_price_at_open']
        result_df['collar_payoff'] = result_df['put_price_at_close'] - result_df['call_price_at_close']
        result_df['collar_pnl'] = result_df['collar_payoff'] - result_df['collar_cost']
        
        return result_df
    

    @ACV.validate_asset_class
    def execute_buy_and_hold_underlying(self, asset_class: str, execution_date: str, execution_price: float, quantity: float, leverage: float=1):
        buy_and_hold = BuyAndHold(self.portfolio, asset_class, self.underlying_asset, self.asset_data)
        buy_and_hold.execute(execution_date, execution_price, quantity, leverage)


    @staticmethod
    def extract_data(row_data):
        data = {
            'current_date': row_data['Date'],
            'call': f"call K={row_data['selected_call_strike']}",
            'put': f"put K={row_data['selected_put_strike']}",
            'call_price_open': row_data['call_price_at_open'],
            'put_price_open': row_data['put_price_at_open'],
            'call_price_close': row_data['call_price_at_close'],
            'put_price_close': row_data['put_price_at_close'],
        }

        return data


    def short_call_long_put(self, row_data):
        data = ZeroCostCollar0DTE.extract_data(row_data)
        n_collar = self.portfolio.positions['equity'][self.underlying_asset]
        self.portfolio.short(date=data['current_date'], asset_class='option', asset=data['call'], price=data['call_price_open'], quantity=n_collar, leverage=1)
        self.portfolio.buy(date=data['current_date'], asset_class='option', asset=data['put'], price=data['put_price_open'], quantity=n_collar, leverage=1)


    def let_0dte_expire(self, row_data):
        data = ZeroCostCollar0DTE.extract_data(row_data)
        put_quantity = self.portfolio.positions['option'][data['put']]
        call_quantity = -self.portfolio.positions['option'][data['call']]       # after the negative sign, call_quantity should be a positive number
        self.portfolio.sell(date=data['current_date'], asset_class='option', asset=data['put'], price=data['put_price_close'], quantity=put_quantity)
        self.portfolio.cover_short(date=data['current_date'], asset_class='option', asset=data['call'], price=data['call_price_close'], quantity=call_quantity)
        

    def execute(self, row_data):
        self.short_call_long_put(row_data)
        self.let_0dte_expire(row_data)

    
'''
    This function is not needed, hedge ratio = number of SPY ETF in portfolio.positions
    def cal_hedge_ratio(self, row_data, option_contract_multiplier, max_daily_loss=0.005):
        """
        Calculate how many collar options we need to hedge the downside risk of holding SPY
        At every market open, the portfolio only has equity and cash, no options
        """
        price_dict = {
            'equity': {
                self.underlying_asset: row_data['Open']
                }
        }
        acceptable_loss = self.portfolio.get_port_value(price_dict) * max_daily_loss
        
        max_loss_per_collar = row_data['Open'] - row_data['selected_put_strike']
        hedge_ratio = acceptable_loss / max_loss_per_collar / option_contract_multiplier

        return hedge_ratio
'''
import pandas as pd

from .strategy import Strategy

class ZeroCostCollar0DTE(Strategy):
    def __init__(self, underlying_data: pd.DataFrame, option_data: pd.DataFrame = None):
        super().__init__(underlying_data, option_data)


    def update_collar_pnl(self, backtest_main_df: pd.DataFrame):
        """
        Only calculates pnl of the option positions (i.e. excluding pnl from holding underlying asset)
        """
        result_df = backtest_main_df.copy()
        result_df['collar_cost'] = result_df['put_price_at_open'] - result_df['call_price_at_open']
        result_df['collar_payoff'] = result_df['put_price_at_close'] - result_df['call_price_at_close']
        result_df['collar_pnl'] = result_df['collar_payoff'] - result_df['collar_cost']
        
        return result_df
    

    def cal_hedge_ratio(portfolio, max_daily_loss=0.005):
        """
        Calculate how many collar options we need to hedge the downside risk of holding SPY
        """

        pass


    def execute(self):
        
        pass
        



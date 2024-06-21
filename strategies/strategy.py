import pandas as pd

from utils import calculate_strike
from portfolio import Portfolio

class Strategy:
    def __init__(self, portfolio: Portfolio, asset: str, asset_data: pd.DataFrame):
        if not isinstance(portfolio, Portfolio):
            raise ValueError("portfolio must be an instance of Portfolio")
        self.portfolio = portfolio
        self.asset = asset
        self.asset_data = asset_data
        self.option_data = None


    def add_option_data(self, option_data):
        self.option_data = option_data


    def select_and_update_options(self, backtest_main_df: pd.DataFrame, selection_rules: dict, option_data: pd.DataFrame):
        """
        this function will select options based on selection_rules defined by users and add option columns to Backtest.main_df by returning result_df
        """
        self.option_data = option_data
        result_df = backtest_main_df.copy()

        for option_type in ['call', 'put']:
            multiplier = selection_rules[option_type + '_K_multiplier']
            method = selection_rules[option_type + '_K_method']
            addition = selection_rules[option_type + '_K_addition']
    
            strikes = result_df[selection_rules['price_base']].apply(
                lambda base: calculate_strike(base, multiplier, addition, method)
            )
            
            col_name = f"selected_{option_type}_strike"
            result_df[col_name] = strikes

            option_df = self.option_data[self.option_data['Option_type'] == option_type]
            temp_df = pd.merge(result_df, option_df,  how='left', left_on=['Date', f"selected_{option_type}_strike"], right_on = ['Date', 'Strike_price'])
            result_df[f"{option_type}_price_at_{selection_rules['price_base'].lower()}"] = temp_df['Option_Value']

        return result_df


    def execute(self, *args, **kwargs):
        raise NotImplementedError("Strategy.execute() should be overridden by specific strategy.")
    

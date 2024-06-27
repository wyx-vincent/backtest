import pandas as pd

from utils import calculate_strike
from portfolio import Portfolio
from backtest import Backtest

class Strategy:
    def __init__(self, portfolio: Portfolio, asset: str, asset_data: pd.DataFrame):
        if not isinstance(portfolio, Portfolio):
            raise ValueError("portfolio must be an instance of Portfolio")
        self.portfolio = portfolio
        self.asset = asset
        self.asset_data = asset_data
        self.option_selection_rules = None
        self.option_data = None


    def add_option_selection_rules(self, selection_rules: dict):
        self.option_selection_rules = selection_rules


    def add_option_data(self, option_data):
        self.option_data = option_data


    def select_options(self, backtest_instance: Backtest, selection_rules: dict):
        """
        this function will select options based on self.option_selection_rules defined by users and add option columns to Backtest.main_df by changing result_df in-place
        """
        self.add_option_selection_rules(selection_rules)

        for option_type in ['call', 'put']:
            multiplier = self.option_selection_rules[option_type + '_K_multiplier']
            method = self.option_selection_rules[option_type + '_K_method']
            addition = self.option_selection_rules[option_type + '_K_adjust']
    
            strikes = backtest_instance.main_df[self.option_selection_rules['base_price']].apply(
                lambda base: calculate_strike(base, multiplier, addition, method)
            )
            
            col_name = f"selected_{option_type}_strike"
            backtest_instance.main_df[col_name] = strikes


    def execute(self, *args, **kwargs):
        raise NotImplementedError("Strategy.execute() should be overridden by specific strategy.")
    



"""
Archived methods

    def select_and_update_options(self, backtest_main_df: pd.DataFrame, selection_rules: dict, option_data: pd.DataFrame):
        '''
        this function will select options based on selection_rules defined by users and add option columns to Backtest.main_df by returning result_df
        '''
        self.option_data = option_data
        result_df = backtest_main_df.copy()

        for option_type in ['call', 'put']:
            multiplier = selection_rules[option_type + '_K_multiplier']
            method = selection_rules[option_type + '_K_method']
            addition = selection_rules[option_type + '_K_adjust']
    
            strikes = result_df[selection_rules['base_price']].apply(
                lambda base: calculate_strike(base, multiplier, addition, method)
            )
            
            col_name = f"selected_{option_type}_strike"
            result_df[col_name] = strikes

            option_df = self.option_data[self.option_data['Option_type'] == option_type]
            temp_df = pd.merge(result_df, option_df,  how='left', left_on=['Date', f"selected_{option_type}_strike"], right_on = ['Date', 'Strike_price'])
            result_df[f"{option_type}_price_at_{selection_rules['base_price'].lower()}"] = temp_df['Option_Value']

        return result_df
"""
    

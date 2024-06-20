import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from portfolio import Portfolio
from strategies.strategy import Strategy


class Backtest:
    def __init__(self, portfolio: Portfolio, underlying_data, option_data=None, buy_leverage=1, sell_leverage=1):
        self.portfolio = portfolio
        self.portfolio.record_date(underlying_data['Date'].values)
        self.main_df = underlying_data.copy()
        self.dates = underlying_data['Date']
        self.option_data = option_data
        self.buy_leverage = buy_leverage
        self.sell_leverage = sell_leverage
        self.issues = []

    
    def add_option_data(self, option_data):
        self.option_data = option_data

    
    def update_option_price_at_close(self):
        self.main_df['call_price_at_close'] = np.maximum(self.main_df['Close'] - self.main_df['selected_call_strike'], 0)
        self.main_df['put_price_at_close'] = np.maximum(self.main_df['selected_put_strike'] - self.main_df['Close'], 0)
        

    # todo: need to rewrite the whole function
    def update_values_temp_func(self):
        self.main_df['spy_overnight_pnl'] = self.main_df['Open'] - self.main_df['Close'].shift(1)
        self.main_df.loc[0, 'spy_overnight_pnl'] = 0
        self.main_df['spy_overnight_return'] =  self.main_df['spy_overnight_pnl'] / self.main_df['Close'].shift(1)
        self.main_df.loc[0, 'spy_overnight_return'] = 0

        self.main_df['spy_intraday_pnl'] = self.main_df['Close'] - self.main_df['Open']
        self.main_df['intraday_pnl'] =  self.main_df['spy_intraday_pnl'] + self.main_df['collar_pnl']
        self.main_df['intraday_return'] = self.main_df['intraday_pnl'] / self.main_df['Open']

        self.main_df['all_pnl'] = self.main_df['intraday_pnl'] - self.main_df['spy_overnight_pnl']
        self.main_df['port_value'] = self.main_df['all_pnl'].cumsum() + self.main_df['Open'].values[0]      # assume invest SPY at open on 1st and no hedge on overnight price changes
        self.main_df['normalized_port_value'] = self.main_df['port_value'] / self.main_df['Open'].values[0]


    def plot_nav_vs_spy(self):
        min_normalized_port_value = np.min(self.main_df['normalized_port_value'].values)
        normalized_spy = self.main_df['Close'] / self.main_df['Open'].values[0]
        date_obj = pd.to_datetime(self.main_df['Date'], format='%m/%d/%y')
        plt.figure(figsize=(16, 8))
        plt.plot(date_obj, self.main_df['normalized_port_value'], color='blue', linestyle='-', label='IMMF')
        plt.plot(date_obj, normalized_spy, color='green', linestyle='-', label='SPY')
        plt.axhline(y=min_normalized_port_value, color='red', linestyle='--', label=f"Min NAV at {round(min_normalized_port_value, 4)}")
        plt.xlabel('Year')
        plt.ylabel('Normalized Portfolio Value')
        plt.grid(True)
        plt.legend()
        plt.show()


    def save_main_df_to_csv(self, filename='backtest_main_df.csv'):
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, 'data', filename)
        self.main_df.to_csv(file_path)


    def run(self, Strategy):
        for index, row in self.main_df.iterrows():
            Strategy.execute(row)



    '''

    def plot_nav_history(self, dates, portfolio_nav_list):
        # Plot NAV history
        plt.figure(figsize=(10, 6))
        plt.plot(dates, portfolio_nav_list, marker='o')
        plt.axhline(y=1, color='r', linestyle='--', label='$1 NAV')
        plt.xlabel('Date')
        plt.ylabel('Portfolio NAV')
        plt.title('Portfolio NAV History')
        plt.grid(True)
        plt.show()
    '''

    def get_issues(self):
        return self.issues



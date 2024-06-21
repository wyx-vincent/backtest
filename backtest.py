import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from portfolio import Portfolio
from strategies.strategy import Strategy


class Backtest:
    def __init__(self, portfolio: Portfolio, asset_data, option_data=None, buy_leverage=1, sell_leverage=1):
        self.portfolio = portfolio
        self.portfolio.record_date(asset_data['Date'].values)
        self.main_df = asset_data.copy()
        self.dates = asset_data['Date']
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


    def plot_nav_vs_spy_archived(self):
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
            price_dict = {'equity': {Strategy.asset: row['Close']}}
            has_asset_class = set(self.portfolio.positions.keys())
            asset_class_in_dict = set(price_dict.keys())
            if has_asset_class != asset_class_in_dict:
                error = (f"Asset classes provided in price_dict are: {asset_class_in_dict}. "
                         f"portfolio contains asset classes: {has_asset_class}.")
                raise ValueError(error)
            self.portfolio.update(price_dict, Strategy.asset)


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


    def calc_benchmark_return(self):
        first_price = pd.Series(self.main_df['Open'][0])
        value_series = self.main_df['Close']
        value_series = pd.concat([first_price, value_series], ignore_index=True)
        return_series = value_series.pct_change().dropna()
        
        return return_series
    

    def generate_dates_series_for_plot(self, length=0):
        first_date = pd.Series(self.dates[0])
        dates_series = self.dates
        dates_series = pd.concat([first_date, dates_series], ignore_index=True)
        dates_series = pd.to_datetime(dates_series, format='%m/%d/%y')
        dates_series = dates_series[0: length]

        return dates_series


    def plot_nav_vs_spy(self):
        port_nav = self.portfolio.nav_history
        min_nav = np.min(port_nav)
        nav_l = len(self.portfolio.nav_history)     # in case we have some errors in backtesting, we can plot what we have

        benchmark_return = self.calc_benchmark_return()
        normalized_benchmark = (1 + benchmark_return).cumprod()
        normalized_benchmark = pd.concat([pd.Series([1]), normalized_benchmark], ignore_index=True)
        normalized_benchmark = normalized_benchmark[0: nav_l]

        dates_series = self.generate_dates_series_for_plot(length=nav_l)

        plt.figure(figsize=(16, 8))
        plt.plot(dates_series, port_nav, color=[0.2, 0.2, 1, 0.9], linestyle='-', label='IMMF')
        plt.plot(dates_series, normalized_benchmark, color=[0.2, 0.7, 0.2, 0.9], linestyle='-', label='SPY')
        plt.axhline(y=min_nav, color='red', linestyle='--', label=f"Min NAV at {round(min_nav, 4)}")
        plt.xlabel('Year')
        plt.ylabel('NAV')
        plt.grid(True)
        plt.legend()
        plt.show()

    
    def plot_exposure(self):

        nav_l = len(self.portfolio.nav_history)
        dates_series = self.generate_dates_series_for_plot(length=nav_l)
    
        equity_exposure = self.portfolio.equity_exposure
        cash_exposure = self.portfolio.cash_exposure

        plt.figure(figsize=(16, 8))
        plt.plot(dates_series, equity_exposure, color=[0.2, 0.2, 1, 0.9], linestyle='-', label='SPY Exposure')
        plt.plot(dates_series, cash_exposure, color=[0.2, 0.7, 0.2, 0.9], linestyle='-', label='Cash Exposure')
        plt.xlabel('Year')
        plt.ylabel('Exposure')
        plt.title('Exposure as a Percentage of Initial Portfolio Nominal Value')
        plt.grid(True)
        plt.legend()
        plt.show()

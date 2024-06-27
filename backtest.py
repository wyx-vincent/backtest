import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
tqdm.pandas()

from portfolio import Portfolio
from utils import generate_option_ticker_vectorized


class Backtest:
    def __init__(self, portfolio: Portfolio, asset_data, data_api, option_data=None):
        self.portfolio = portfolio
        self.portfolio.record_date(asset_data['Date'].values)
        self.main_df = asset_data.copy()    # backtest details for all days, length = number of days
        self.data_api = data_api
        self.dates = asset_data['Date']
        self.option_data = option_data      # option chain data for all days, length = number of days * number of available/choosen options on each day
        self.issues = []

    
    def add_option_data(self, option_data):
        self.option_data = option_data


    def get_option_price_bs(self, option_data: pd.DataFrame, spot_price: str):
        """
        this function will search option prices from option_data (generated by BS model) and add option price columns to Backtest.main_df
        """
        self.add_option_data(option_data)

        for option_type in ['call', 'put']:
            sub_df = self.option_data[self.option_data['Option_type'] == option_type]
            temp_df = pd.merge(self.main_df, sub_df,  how='left', left_on=['Date', f"selected_{option_type}_strike"], right_on = ['Date', 'Strike_price'])
            self.main_df[f"{option_type}_price_at_{spot_price.lower()}"] = temp_df['Option_Value']


    def update_option_price_at_expiration(self):
        self.main_df['call_price_at_close'] = np.maximum(self.main_df['Close'] - self.main_df['selected_call_strike'], 0)
        self.main_df['put_price_at_close'] = np.maximum(self.main_df['selected_put_strike'] - self.main_df['Close'], 0)


    def save_main_df_to_csv(self, filename='backtest_main_df.csv'):
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, 'data', filename)
        self.main_df.to_csv(file_path)


    def run(self, Strategy, simulation_days=None):
        if simulation_days is None:
            simulation_days = len(self.main_df)
            
        start_index = self.main_df.index[0]
        end_index = start_index + simulation_days - 1
        if end_index > self.main_df.index[-1]:
            end_index = self.main_df.index[-1]

        for index, row in self.main_df.loc[start_index:end_index].iterrows():
            Strategy.execute(row)
            price_dict = {'equity': {Strategy.asset: row['Close']}}
            has_asset_class = set(self.portfolio.positions.keys())
            asset_class_in_dict = set(price_dict.keys())
            if has_asset_class != asset_class_in_dict:
                error = (f"Asset classes provided in price_dict are: {asset_class_in_dict}. "
                         f"portfolio contains asset classes: {has_asset_class}.")
                raise ValueError(error)
            self.portfolio.update(price_dict, Strategy.asset)


    def get_issues(self):
        return self.issues


    def calc_benchmark_return(self):
        first_price = pd.Series(self.main_df['Open'].values[0])
        value_series = self.main_df['Close']
        value_series = pd.concat([first_price, value_series], ignore_index=True)
        return_series = value_series.pct_change().dropna()
        
        return return_series
    

    def generate_dates_series_for_plot(self, length=0):
        first_date = pd.Series(self.dates.values[0])
        dates_series = self.dates
        dates_series = pd.concat([first_date, dates_series], ignore_index=True)
        dates_series = pd.to_datetime(dates_series, format='%Y-%m-%d')
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


    def generate_option_parameters(self, underlying_ticker, spot_price_col, strike_bound_config=None):
        spot_price_col = spot_price_col.title()
        
        if strike_bound_config:
            # corresponds to strategy 1
            # For a specific day, generate calls first, then puts
            spot_prices = self.main_df[spot_price_col].values
            lower_values = spot_prices * (1 + strike_bound_config['lower_bound'])
            upper_values = spot_prices * (1 + strike_bound_config['upper_bound'])
            strike_ranges = [np.arange(int(low), int(high) + 1) for low, high in zip(lower_values, upper_values)]
            n_strikes = [len(strikes) for strikes in strike_ranges]
            expanded_strike_ranges = [np.tile(strikes, 2) for strikes in strike_ranges]  # expand for call and put. This is also the total number of options on each day
            strikes = np.concatenate(expanded_strike_ranges)                            # total number of rows in the entire option chain data
            option_types = np.concatenate([np.repeat(['call', 'put'], [n, n]) for n in n_strikes])
            dates = np.repeat(self.main_df['Date'].values, [len(r) for r in expanded_strike_ranges])
            spot_prices = np.repeat(self.main_df[spot_price_col].values, [len(r) for r in expanded_strike_ranges])
            indices = np.repeat(self.main_df.index, [len(r) for r in expanded_strike_ranges])

        else:
            # corresponds to strategy 2
            # Generate all calls together for all days first, then all puts
            call_strikes = self.main_df['selected_call_strike'].values
            put_strikes = self.main_df['selected_put_strike'].values
            strikes = np.concatenate([call_strikes, put_strikes])
            option_types = np.array(['call'] * len(call_strikes) + ['put'] * len(put_strikes))
            dates = np.tile(self.main_df['Date'].values, 2)
            spot_prices = np.tile(self.main_df[spot_price_col].values, 2)
            indices = np.tile(self.main_df.index, 2)

        underlying_tickers = np.array([underlying_ticker] * len(strikes))
        option_tickers = generate_option_ticker_vectorized(underlying_tickers, dates, option_types, strikes)

        option_data = pd.DataFrame({
            'option_tickers': option_tickers,
            'date_from': dates,
            'date_to': dates,
            'option_type': option_types,
            'strike': strikes,
            'spot_price': spot_prices,
            'main_df_index': indices
            })
        
        self.add_option_data(option_data)
                


    def get_option_price(self, underlying_ticker: str, bs_config: dict, open_price_config, strike_bound_config: dict=None, ): 
        
        """
        Fetch the price of a 0DTE (Zero Days to Expiration) option at market open using the Polygon.io API.
        If price data is not available on Polygon.io, the BS model will be used to calculate price, which will print relevant info
        
        Parameters
        ----------
        underlying_ticker : str
            The ticker of the underlying asset for the option.

        spot_price_col: str, optional
            The column in backtest's main_df that would be used as spot price in the BS model. This is also the time point used to fetch price data
    
        strike_bound_config:
        
        bar_multiplier : int, optional
            The duration of each bar in bar_timespan. This defines the time span for the aggregated bar data. Default is 3 seconds.
        
        bar_timespan : str, optionl
            The time span of a bar data, Possible values are second, minute, hour, day

        price_type : str, optional
            The price type used to determine the market ”opening price“. Possible values are 'open', 'high', 'low', 'close', and 'vwap'. Default is 'vwap'.
            'vwap' is the volume weighted average price, calculated by dividing the total dollar amount traded by the total volume traded during a bar.

        Example
        -------
        If `bar_multiplier` is set to 3 and `price_type` is 'vwap', the function will return the volume weighted average price within the first 3 seconds after the market opens at 9:30 AM ET.
        """
        
        self.generate_option_parameters(underlying_ticker, bs_config['spot_price_col'], strike_bound_config)
        self.option_data, bs_days = self.data_api.try_get_polygon_price_multithread(self.option_data, open_price_config['bar_multiplier'], open_price_config['bar_timespan'], open_price_config['price_type'], bs_config)
       
        for option_type in ['call', 'put']:
            col_name = f"{option_type}_price_at_open"
            self.main_df[col_name] = np.nan

        for index, row in self.option_data.iterrows():
            main_df_index = row['main_df_index']
            option_type = row['option_type']
            price = row['open_price']
            column_name = f"{option_type}_price_at_open"
            self.main_df.at[main_df_index, column_name] = price
    
        if bs_days:
            print('')
            print("Used BS model on the following days and options:")
            for day in bs_days:
                print(day)
        else:
            print("BS model is not used. All prices are sourced from Polygon.io.")




    """
    The followings are archived functions

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

    """
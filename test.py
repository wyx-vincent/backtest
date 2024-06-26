
from tqdm.notebook import tqdm
tqdm.pandas()

from portfolio import Portfolio
from backtest import Backtest
from strategies import *
from config import *
from utils import PolygonAPI
from data_processing import *

spy_df = get_spy_data(start_date, end_date)

# instantiation
my_portfolio = Portfolio(initial_portfolio_nominal_value, portolio_weights_config, collateral_ratio)
my_strategy = ZeroCostCollar0DTE(my_portfolio, 'SPY', spy_df)
env = Backtest(my_portfolio, spy_df, PolygonAPI(api_key='MPkBRXXyfleZXSJQp8_bOsKuqo2Wi_Gk'))

# If price data is not available on Polygon.io, the BS model will be used to calculate price, which will print relevant info
if strategy == 1:
    my_strategy.add_zero_cost_collar(env, zero_cost_search_config, bs_config, 3, 'second', 'vwap')
elif strategy == 2:
    # select options based on config.strike_selection_config
    env.main_df = my_strategy.select_options(env.main_df, strike_selection_config)
    prices, bs_days = env.get_option_price('SPY', 3, 'second', 'vwap', 'open', bs_config)
else:
    raise ValueError("Check config, strategy does not exist. ")


options_list = [
    {
        'option_tickers': 'O:SPY240620C00550000',
        'date_from': '2024-06-20',
        'date_to': '2024-06-20',
        'option_type': 'call',
        'strike': 550,
        'spot_price': 550,
        'bs_config': bs_config
    },
    {
        'option_tickers': 'O:SPY240620P00550000',
        'date_from': '2024-06-20',
        'date_to': '2024-06-20',
        'option_type': 'put',
        'strike': 550,
        'spot_price': 550,
        'bs_config': bs_config
    }
]

env.main_df = my_strategy.select_options(env.main_df, strike_selection_config)
env.add_options_list('SPY', 'Open')
print(len(env.options_list))
prices_dict, bs_days = env.data_api.try_get_polygon_price_multithread(env.options_list, 3, 'second', 'vwap', bs_config)

print(prices)


for index, row in env.main_df.iterrows():
    print(index)

import numpy as np
np.tile(np.array([10, 2, 3]), 2)

def slicer_vectorized(a, start, end):
    # ref: https://stackoverflow.com/questions/39042214/how-can-i-slice-each-element-of-a-numpy-array-of-strings
    b = a.view((str,1)).reshape(len(a), -1)[:, start:end]
    return np.array(b).view((str,end-start)).flatten()
    # this will also work: return np.fromstring(b.tobytes(), dtype=(str, end-start))


option_types = ['call', 'put', 'abc']
not np.all(np.isin(option_types, ['call', 'put']))
underlying_tickers = ['SPY', 's', 'np', 'abC']
dates = ['2020-01-01', '2024-06-22', '2023-01-01']
underlying_ticker_str = np.char.upper(underlying_tickers)
date_str = np.char.replace(dates, '-', '')
date_str = slicer_vectorized(date_str, 2, 8)


strikes = np.array([100, 300, 500, 545, 333.5])
strike_scaled = strikes * 1000
strike_str = np.char.zfill(np.char.mod('%d', strike_scaled).astype(str), 8)


def generate_option_ticker_vectorized(underlying_tickers, dates, option_types, strikes):
    if not np.all(np.isin(option_types, ['call', 'put'])):
        raise ValueError("some option type values are wrong, please use either 'call' or 'put' in option_types.")
    
    underlying_ticker_str = np.char.upper(underlying_tickers)
    date_str = np.char.replace(dates, '-', '')
    date_str = slicer_vectorized(date_str, 2, 8)
    type_str = slicer_vectorized(option_types, 0, 1)
    strike_scaled = strikes * 1000
    strike_str = np.char.zfill(np.char.mod('%d', strike_scaled).astype(str), 8)

    tickers = 'O:' + underlying_ticker_str + date_str + type_str + strike_str

    return tickers
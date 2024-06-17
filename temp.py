import os
import time

import pandas as pd

from option_functions import *

current_dir = os.getcwd()
spy_data_path = os.path.join(current_dir, 'data', 'SPY.csv')
spy_data = pd.read_csv(spy_data_path)

q = 0
vol = 0.2               # assume constant vol
r = 0.05
lower_K_factor = 0.9    # min strike price will be int(open * lower_K_factor)
upper_K_factor = 1.1    # max strike price will be int(open * upper_K_factor)

strike_ranges = [np.arange(start=int(open_price * lower_K_factor), stop=int(open_price * upper_K_factor) + 1) for open_price in spy_data['Open']]
n_strikes = [len(strikes) for strikes in strike_ranges]
strike_ranges = [np.tile(strikes, 2) for strikes in strike_ranges]  # prepare for call and put
strikes = np.concatenate(strike_ranges)
repeated_dates = np.repeat(spy_data['Date'], [len(r) for r in strike_ranges])
repeated_open = np.repeat(spy_data['Open'], [len(r) for r in strike_ranges])
repeated_close = np.repeat(spy_data['Close'], [len(r) for r in strike_ranges])
option_types = np.concatenate([np.repeat(['call', 'put'], [n, n]) for n in n_strikes])

open_options_df = pd.DataFrame({
    'Date': repeated_dates,
    'Open_price': repeated_open,
    'Option_type': option_types,
    'Strike_price': strikes,
    'Volatility': np.ones(len(repeated_dates)) * vol,
    'Rf': np.ones(len(repeated_dates)) * r,
    'Dividend_yield': np.zeros(len(repeated_dates)),
    'Time_to_expiration': np.ones(len(repeated_dates)) * (1/365),
    'Option_Value': np.nan})

def apply_option_pricing(row):
    K = row['Strike_price']
    S = row['Open_price']
    T = row['Time_to_expiration']
    vol = row['Volatility']
    r = row['Rf']
    q = row['Dividend_yield']
    option_type = row['Option_type']

    return blackscholes_price(K, T, S, vol, r, q, callput=option_type)


t1 = time.time()
open_options_df['Option_Value'] = open_options_df.apply(apply_option_pricing, axis=1)
t2 = time.time()
print('Time used for calculating option price', t2-t1)


call_values = np.maximum(repeated_close.values - strikes, 0)
put_values = np.maximum(strikes - repeated_close.values, 0)
close_option_values = np.where(option_types == 'call', call_values, put_values)

close_options_df = pd.DataFrame({
    'Date': repeated_dates,
    'Close_price': repeated_close,
    'Option_type': option_types,
    'Strike_price': strikes,
    'Option_Value': close_option_values})



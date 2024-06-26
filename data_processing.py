import os

import pandas as pd
import numpy as np
import time

from config import *
from utils.option_functions import blackscholes_price
from utils import convert_date_format



def get_spy_data(start_date, end_date):
    current_dir = os.getcwd()
    spy_data_path = os.path.join(current_dir, 'data', 'SPY.csv')
    spy_data = pd.read_csv(spy_data_path)
    filtered_spy_data = spy_data[(spy_data['Date'] >= start_date) & (spy_data['Date'] <= end_date)]

    return filtered_spy_data


def generate_option_chain(underlying_price_df: pd.DataFrame, bs_config: dict, lower_K_multiplier: float = 0.95, upper_K_multiplier: float = 1.05, spot_price: str = 'open') -> pd.DataFrame:
    """
    Returns a DataFrame of option chain data for every time step in underlying_price_df
    This structure introduces some level of redundancy and does not strictly adhere to the Fourth Normal Form (4NF), 
    in order to prioritize readability by reducing the data dimension

    Parameters
    --------
    underlying_price_df: pd.DataFrame
        a DataFrame object containing the Open, High, Low, Close, Adj Close, Volume data of an underlying asset

    bs_config: dict
        Black Scholes model parameters assumptions
        contains 'q', 'vol', 'r', 'time_to_expiration'
       
    lower_K_multiplier: float
       The lower bound multiplier used to list option strike prices.
       Lower bound strike = int(open_price * lower_K_multiplier)

    upper_K_multiplier: float
       The upper bound multiplier used to list option strike prices.
       Upper bound strike = int(open_price * lower_K_multiplier)

    spot_price: str
        Specifies the price point ('open', 'high', 'low', 'close', or adj close') on which to base the calculations. Defaults to 'open'.

    """
    spot_price = spot_price.title()
    strike_ranges = [np.arange(start=int(price * lower_K_multiplier), stop=int(price * upper_K_multiplier) + 1) for price in underlying_price_df[generate_at]]
    n_strikes = [len(strikes) for strikes in strike_ranges]
    strike_ranges = [np.tile(strikes, 2) for strikes in strike_ranges]  # prepare for call and put
    flat_strikes = np.concatenate(strike_ranges)
    repeated_dates = np.repeat(underlying_price_df['Date'], [len(r) for r in strike_ranges])
    repeated_price = np.repeat(underlying_price_df[spot_price], [len(r) for r in strike_ranges])
    option_types = np.concatenate([np.repeat(['call', 'put'], [n, n]) for n in n_strikes])

    option_chain_df = pd.DataFrame({
    'Date': repeated_dates,
    spot_price + '_price': repeated_price,
    'Option_type': option_types,
    'Strike_price': flat_strikes,
    'Volatility': np.ones(len(repeated_dates)) * bs_config['vol'],
    'Rf': np.ones(len(repeated_dates)) * bs_config['r'],
    'Dividend_yield': np.ones(len(repeated_dates)) * bs_config['q'],
    'Time_to_expiration': np.ones(len(repeated_dates)) * bs_config['time_to_expiration'],
    'Option_Value': np.nan}
    )

    option_chain_df = option_chain_df.reset_index(drop=True)

    t1 = time.time()
    
    option_chain_df['Option_Value'] = option_chain_df.apply(
        lambda row: blackscholes_price(
            K = row['Strike_price'],
            S = row[spot_price + '_price'],
            T = row['Time_to_expiration'],
            vol = row['Volatility'],
            r = row['Rf'],
            q = row['Dividend_yield'],
            callput = row['Option_type']
        ), 
        axis=1
    )

    t2 = time.time()
    print(f"Time used for calculating option prices {round(t2-t1, 4)} seconds.")

    return option_chain_df




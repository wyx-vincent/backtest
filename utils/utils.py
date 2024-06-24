import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Dict
from utils.polygon_functions import get_0DTE_price_at_open, DataNotAvailableError
from utils import blackscholes_price


def find_indices_closest_to_zero_sum(a, b):

    """
    Returns the indices of exactly one element from each of two arrays (a and b) such that the sum of these two elements is the closest to zero.
    Complexity: O(nlogn)
    """

    # Sort array b but keep the original indices
    b_sorted_indices = np.argsort(b)
    b_sorted = b[b_sorted_indices]
    
    closest_sum = float('inf')
    closest_pair_indices = (None, None)
    
    # Iterate through each element in array a
    for i, num_a in enumerate(a):
         # Binary search in b_sorted for the value closest to -num_a
        low, high = 0, len(b_sorted) - 1
        while low <= high:
            mid = (low + high) // 2
            num_b = b_sorted[mid]
            current_sum = num_a + num_b
            
            # Update the closest sum and indices if the current sum is closer to zero
            if abs(current_sum) < abs(closest_sum):
                closest_sum = current_sum
                closest_pair_indices = (i, b_sorted_indices[mid])
            
            # If the current sum is exactly zero, return immediately
            if current_sum == 0:
                return closest_pair_indices
                break
            elif current_sum < 0:
                low = mid + 1
            else:
                high = mid - 1
    
    return closest_pair_indices


def get_0DTE_open_price_given_strikes(
        underlying_ticker: str, 
        strikes: List[int],
        date: str,
        spot_price: float, 
        bs_config: Dict[str, float],
        bar_multiplier: int=3, 
        bar_timespan: str='second', 
        price_type: str='vwap',
        ) -> Dict[str, List]:
    result = {'strikes': strikes, 'call': [], 'put': []}
    for option_type in ['call', 'put']:
        for strike in strikes:
            try:
                price = get_0DTE_price_at_open(underlying_ticker, option_type, strike, date, bar_multiplier, bar_timespan, price_type)
            except DataNotAvailableError:
                price = blackscholes_price(K=strike, S=spot_price, T=bs_config['time_to_expiration'], vol=bs_config['vol'], r=bs_config['r'], q=bs_config['q'], callput=option_type)
            result[option_type].append(price)

    return result


def calculate_strike(base, multiplier, addition, method='floor'):
    """
    Retrieve a numpy method based on the method name with a default to np.floor.
    Calculate the strike price using a base price, method, multiplier, and addition.
    """
    func = getattr(np, method, np.floor)
    return func(base * multiplier) + addition


def try_get_polygon_price(underlying_ticker, option_type, row, bar_multiplier, bar_timespan, price_type, spot_price, bs_config, bs_days):
    try:
        return get_0DTE_price_at_open(
            underlying_ticker,
            option_type,
            strike=row['selected_' + option_type + '_strike'],
            date=row['Date'],
            bar_multiplier=bar_multiplier,
            bar_timespan=bar_timespan,
            price_type=price_type
        )
    except DataNotAvailableError:
        bs_days.append(f"{row['Date']} for {option_type}, K={row['selected_' + option_type + '_strike']}")
        return blackscholes_price(
            K=row['selected_' + option_type + '_strike'],
            S=row[spot_price.title()],
            T=bs_config['time_to_expiration'],
            vol=bs_config['vol'],
            r=bs_config['r'],
            q=bs_config['q'],
            callput=option_type
        )


def plot_distribution(data, x_label, title, bins=30, color='blue'):
    plt.hist(data, bins=bins, color=color, alpha=0.7)
    plt.grid(True)
    plt.xlabel(x_label)
    plt.ylabel('Frequency')
    plt.title(title)
    plt.show()


def convert_date_format(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
    """
    Convert the dates in the specified column of the DataFrame to the 'yyyy-mm-dd' format.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the date column to be converted.
    date_column : str
        The name of the column containing dates to be converted.

    Returns
    -------
    pd.DataFrame
        The DataFrame with the dates in the specified column converted to 'yyyy-mm-dd' format.
    """

    df[date_column] = pd.to_datetime(df[date_column], format='%m/%d/%y')
    df[date_column] = df[date_column].dt.strftime('%Y-%m-%d')

    return df


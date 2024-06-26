import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def calculate_strike(base, multiplier, addition, method='floor'):
    """
    Retrieve a numpy method based on the method name with a default to np.floor.
    Calculate the strike price using a base price, method, multiplier, and addition.
    """
    func = getattr(np, method, np.floor)
    return func(base * multiplier) + addition


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


def generate_option_ticker(underlying_ticker, date, option_type, strike):
    if option_type not in ['call', 'put']:
        raise ValueError("option type input is wrong, please use either 'call' or 'put'. ")
    underlying_ticker_str = underlying_ticker.upper()
    date_str = date.replace('-', '')[2:]
    type_str = option_type[0].upper()
    strike_str = f"{int(strike*1000):08d}"
    ticker = 'O:' + underlying_ticker_str + date_str + type_str + strike_str

    return ticker


def slicer_vectorized(a, start, end):
    # ref: https://stackoverflow.com/questions/39042214/how-can-i-slice-each-element-of-a-numpy-array-of-strings
    b = a.view((str,1)).reshape(len(a), -1)[:, start:end]
    return np.array(b).view((str,end-start)).flatten()
    # this will also work: return np.fromstring(b.tobytes(), dtype=(str, end-start))


def generate_option_ticker_vectorized(underlying_tickers, dates, option_types, strikes):
    if not np.all(np.isin(option_types, ['call', 'put'])):
        raise ValueError("some option type values are wrong, please use either 'call' or 'put' in option_types.")
    
    underlying_ticker_str = np.char.upper(underlying_tickers)
    date_str = dates.astype(str)
    date_str = np.char.replace(date_str, '-', '')
    date_str = slicer_vectorized(date_str, 2, 8)
    type_str = np.char.upper(option_types)
    type_str = slicer_vectorized(type_str, 0, 1)
    strike_scaled = strikes * 1000
    strike_str = np.char.zfill(np.char.mod('%d', strike_scaled).astype(str), 8)


    tickers = np.core.defchararray.add('O:', underlying_ticker_str) 
    for str_arr in [date_str, type_str, strike_str]:
        tickers = np.core.defchararray.add(tickers, str_arr)

    return tickers





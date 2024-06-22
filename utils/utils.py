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


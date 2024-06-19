import numpy as np
import matplotlib.pyplot as plt

def calculate_strike(base, multiplier, offset, method='floor'):
    """
    Retrieve a numpy method based on the method name with a default to np.floor.
    Calculate the strike price using a base price, method, multiplier, and offset.
    """
    func = getattr(np, method, np.floor)
    return func(base * multiplier) + offset


def plot_distribution(data, x_label, title, bins=30, color='blue'):
    plt.hist(data, bins=bins, color=color, alpha=0.7)
    plt.grid(True)
    plt.xlabel(x_label)
    plt.ylabel('Frequency')
    plt.title(title)
    plt.show()
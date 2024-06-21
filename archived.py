import os
import time

import pandas as pd
import matplotlib.pyplot as plt


from utils.option_functions import *


"""
Archived work, do not run this file

"""





'''

def add_option_strikes_col(df):
    df['put_strike'] = np.floor(df['Open'])-4
    df['call_strike'] = np.floor(df['Open'] * 1.005)
    return df

def add_option_price_col(df, all_option_df, option_type='call'):
    option_df = all_option_df[all_option_df['Option_type'] == option_type]
    temp_df = pd.merge(df, option_df,  how='left', left_on=['Date',option_type + '_strike'], right_on = ['Date','Strike_price'])
    df[option_type + '_price'] = temp_df['Option_Value']
    return df

backtest_df = spy_data.copy()
backtest_df = add_option_strikes_col(backtest_df)

backtest_df = add_option_price_col(backtest_df, open_options_df, option_type='call')
backtest_df = add_option_price_col(backtest_df, open_options_df, option_type='put')

backtest_df['collar_cost'] = backtest_df['put_price'] - backtest_df['call_price']
backtest_df['call_value_at_close'] = np.maximum(backtest_df['Close'] - backtest_df['call_strike'], 0)
backtest_df['put_value_at_close'] = np.maximum(backtest_df['put_strike'] - backtest_df['Close'], 0)
backtest_df['collar_payoff'] = backtest_df['put_value_at_close'] - backtest_df['call_value_at_close']
backtest_df['collar_profit'] = backtest_df['collar_payoff'] - backtest_df['collar_cost']


plt.hist(backtest_df['collar_cost'], bins=40, color='blue', alpha=0.7)
plt.grid(True)
plt.show()


n_collar = 1
backtest_df['overnight_pnl'] = backtest_df['Open'] - backtest_df['Close'].shift(1)
backtest_df.loc[0, 'overnight_pnl'] = 0
backtest_df['overnight_return'] =  backtest_df['overnight_pnl'] / backtest_df['Close'].shift(1)
backtest_df.loc[0, 'overnight_return'] = 0
backtest_df['spy_daily_pnl'] = backtest_df['Close'] - backtest_df['Open']
backtest_df['r'] =  backtest_df['spy_daily_pnl'] + backtest_df['collar_profit']
backtest_df['rp'] = backtest_df['r']/backtest_df['Open']
backtest_df['daily_pnl']= backtest_df['spy_daily_pnl'] + backtest_df['collar_profit'] # - backtest_df['overnight_pnl']
backtest_df['port_value'] = backtest_df['daily_pnl'].cumsum() + backtest_df['Open'].values[0]
# = backtest_df['Close'] + backtest_df['collar_profit'] - backtest_df['overnight_pnl']
backtest_df['normalized_port_value'] = backtest_df['port_value'] / backtest_df['Open'].values[0]
normalized_spy = backtest_df['Close'] / backtest_df['Open'].values[0]


min_normalized_port_value = np.min(backtest_df['normalized_port_value'].values)
date_obj = pd.to_datetime(backtest_df['Date'])
plt.figure(figsize=(16, 8))
plt.plot(date_obj, backtest_df['normalized_port_value'], color='blue', linestyle='-', label='IMMF')
plt.plot(date_obj, normalized_spy, color='green', linestyle='-', label='SPY')
plt.axhline(y=min_normalized_port_value, color='red', linestyle='--', label=f"Min NAV at {round(min_normalized_port_value, 4)}")
plt.xlabel('Year')
plt.ylabel('Normalized Portfolio Value')
plt.grid(True)
plt.legend()
plt.show()


plt.hist(backtest_df['rp'], bins=50, color='blue', alpha=0.7)
plt.grid(True)
plt.xlabel('Daily return during trading hours')
plt.ylabel('Frequency')
plt.title('Daily Percentage Return Distribution')
plt.show()

plt.hist(backtest_df['overnight_return'], bins=40, color='blue', alpha=0.7)
plt.grid(True)
plt.show()

np.min(backtest_df['overnight_return'].values)

backtest_df.to_csv('backtest_df.csv', index=True)

'''

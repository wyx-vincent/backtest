start_date = '2022-07-01'               # It seems like polygon.io doesn’t have all 0DTE data until 2022-11-10.
end_date = '2024-06-25'

initial_portfolio_nominal_value = 1e6 
collateral_ratio = 1                    # collateral_ratio: the ratio of total assets deposited to initial_portfolio_nominal_value. The portion that is larger than 1 will be used as cash
portolio_weights_config = {             # this is just initial weights, have not implement weight_check function and rebalance function
    'equity': 0.5,
    'cash': 0.5,
}

# option parameters
bs_config = {
    'q': 0,                                   # dividend yield in Black–Scholes model, will use discrete dividends
    'vol': 0.2,                               # assume constant vol, a higher constant vol would significantly underprices collar cost and overprices its payoff
    'r': 0.05,                                # assume constant risk-free rate
    'time_to_expiration': 1/365,              # 0DTE
    'spot_price_col': 'open'                  
}

open_price_config = {
    'bar_multiplier': 3, 
    'bar_timespan': 'second', 
    'price_type': 'vwap'
}

strategy_selected = 1

# strategy 1: Find the collar strategy (short call + long put) whose cost closest to zero cost based on the opening prices of SPY and 0DTE.
zero_cost_search_config = {
    'upper_bound': 0.002,
    'lower_bound': -0.002
}


# strategy 2: Select call and put strike prices based on the settings below.
strike_selection_config = {
    'base_price': 'Open',               # The base price type from which the strike prices are calculated. Example: 'Open' or 'Close'.

    'put_K_multiplier': 0.97,            # Multiplier applied to the base price before rounding to determine put strike price.
    'put_K_method': 'floor',            # Method to round the calculated put strike price. Options: 'floor' or 'ceil'.
    'put_K_addition': 0,               # Numeric addition added after rounding to adjust the put strike price.
                                        # Example: put strike = floor(df['Open'] * 1) + (-4)
    'call_K_multiplier': 1.03,
    'call_K_method': 'floor',
    'call_K_addition': 0                 # Example: call strike = floor(df['Open'] * 1.005) + 0
}


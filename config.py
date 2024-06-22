start_date = '2022-11-11'               # It seems like polygon.io doesn’t have all 0DTE data until 2022-11-10.
end_date = '2024-06-21'

initial_portfolio_nominal_value = 1e6 
collateral_ratio = 1                    # collateral_ratio: the ratio of total assets deposited to initial_portfolio_nominal_value. The portion that is larger than 1 will be used as cash
portolio_weights_config = {             # this is just initial weights, have not implement weight_check function and rebalance function
    'equity': 0.75,
    'cash': 0.25,
    'option': 0,                        # not used for now
    'mmf': 0                            # not used for now
}


# 0DTE strike selection
strike_selection_config = {
    'base_price': 'Open',               # The base price type from which the strike prices are calculated. Example: 'Open' or 'Close'.

    'put_K_multiplier': 1.0,            # Multiplier applied to the base price before rounding to determine put strike price.
    'put_K_method': 'floor',            # Method to round the calculated put strike price. Options: 'floor' or 'ceil'.
    'put_K_addition': -4,               # Numeric addition added after rounding to adjust the put strike price.
                                        # Example: put strike = floor(df['Open'] * 1) + (-4)
    'call_K_multiplier': 1.005,
    'call_K_method': 'floor',
    'call_K_addition': 0                 # Example: call strike = floor(df['Open'] * 1.005) + 0
}


# option parameters
bs_config = {
    'q': 0,                                   # dividend yield in Black–Scholes model, will use discrete dividends
    'vol': 0.2,                               # assume constant vol, a higher constant vol would significantly underprices collar cost and overprices its payoff
    'r': 0.05,                                # assume constant risk-free rate
    'time_to_expiration': 1/365               # 0DTE
}

option_contract_multiplier = 100        # not used for now, the number of shares an options contract represents

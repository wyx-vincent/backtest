# Current portfolio assumption: 
# 1) Only buy and hold one share of SPY at market open on the first day
# 2) Enter a collar using 0DTE, and let it expire at market close. 
# 3) The costs of entering a collar strategy are negligible, as most of them are negative
# 4) ETF dividends were not included in calculation
# 5) No fund distribution/payout to fund investors
# 6) Overnight cost changes are not hedged
portfolio_initial_cash = 1000000        # unused for now 


# option parameters
q = 0                                   # dividend yield in Black–Scholes model, will use discrete dividends
vol = 0.2                               # assume constant vol
r = 0.05                                # assume constant risk-free rate
time_to_expiration = 1/365              # 0DTE


# 0DTE strike selection
strike_selection_config = {
    'price_base': 'Open',               # The base price type from which the strike prices are calculated. Example: 'Open' or 'Close'.

    'put_K_multiplier': 1,              # Multiplier applied to the base price before rounding to determine put strike price.
    'put_K_method': 'floor',            # Method to round the calculated put strike price. Options: 'floor' or 'ceil'.
    'put_K_offset': -4,                 # Numeric offset added after rounding to adjust the put strike price.
                                        # Example: put strike = floor(df['Open'] * 1 - 4
    'call_K_multiplier': 1.005,
    'call_K_method': 'floor',
    'call_K_offset': 0                  # Example: call strike = floor(df['Open'] * 1.005 - 0
}



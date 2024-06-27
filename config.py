start_date = '2022-12-01'
end_date = '2024-06-25'

# Portfolio Configuration
initial_portfolio_nominal_value = 1e6
collateral_ratio = 1
portolio_weights_config = {
    'equity': 0.8,
    'cash': 0.2,
}

strategy_selected = 1

# For Strategy 1
zero_cost_search_config = {
    'upper_bound': 0.005,
    'lower_bound': -0.005
}

# For Strategy 2
strike_selection_config = {
    'base_price': 'Open',

    'put_K_multiplier': 0.99,
    'put_K_method': 'floor',
    'put_K_adjust': 0,

    'call_K_multiplier': 1.02,
    'call_K_method': 'floor',
    'call_K_adjust': 0
}

# Black-Scholes Model Assumptions
bs_config = {
    'q': 0,
    'vol': 0.15,
    'r': 0.05,
    'time_to_expiration': 1/365,
    'spot_price_col': 'open'        
}

# Option Open Price Reference
open_price_config = {
    'bar_multiplier': 3, 
    'bar_timespan': 'second', 
    'price_type': 'vwap'
}

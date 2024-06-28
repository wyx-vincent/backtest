# Backtest Framework for Multiple Investment Strategies

One of the objectives of this project is to provide a general framework for backtesting various investment strategies. Any functions or methods related to objective market conditions, such as data queries, price updates, and benchmark returns, are contained within the **Backtest** class. Anything related to subjective strategies, such as when to buy or sell assets, how to select options, and how to determine the range within which to search for a zero-cost collar, is located in the **Strategy** class or its child classes. All records or data related to the investment portfolio during the backtesting process, such as cash, positions, margin, and transaction history, are maintained in the **Portfolio** class.

<br>

# Innovative Money Market Fund (IMMF) 

## Introduction
The core objective of this project is to investigate whether we can create a new form of money market fund, where the NAV never drops below $1.00 (specifically, never below $0.995), by holding SP500 ETFs (SPY) long-term, related short-term or long-term options (0DTE, LEAPS, etc.), as well as cash and cash equivalents (invested in traditional MMF). This fund can be used to track the value of U.S. dollars while providing investors with exposure to SP500. Currently, this project does not account for the legal requirements and regulatory restrictions.

## Portfolio Assumptions 
- Long-term Holding Strategy: The portfolio will maintain a long-term position in SPY, with a rebalancing strategy to be discussed and implemented.
- Collar Strategy Implementation: The portfolio implements a daily collar strategy (short call and long put) using 0DTE options at market open, with positions expiring at market close. This strategy is designed to hedge the daily price changes in SPY.
- Interest Rates: An interest rate of zero is assumed for activities involving short selling and purchasing with leverage.
- Leverage and Borrowing: While the code supports asset purchases with leverage, the borrowing limits are yet to be defined.
- Short Selling: Short selling is permitted when the portfolio's cash balance exceeds the required margin. Proceeds from short selling are held in an isolated margin account. Upon covering a short position, the cash in its margin account is released, i.e., transferred back to the cash account.
- Dividend Policy: Dividends from ETFs are not received currently (implementation pending).
- Fund Distributions: There are no distributions or payouts to fund investors.
- Over-collateralization: The code supports over-collateralization by fund investors. Any amount exceeding a collateral ratio of 1 is treated as cash within the portfolio.
- Cost Considerations: There are no transaction fees considered.
- Other Risk Exposures: 
    1. Overnight price changes in SPY are not hedged.
    2. No margin call or liquidation process.
    3. The impact of bid-ask spread, slippage, and liquidity is not considered. Prices from datasets or APIs are assumed to represent actual execution prices in our strategies.


## Strategies
1. Searching for Zero-cost Collar 
This strategy involves finding a call and put option pair that approximates zero cost, based on the open prices of SPY and 0DTE options. Given the practical constraints of trade execution at market open, users of this project have the flexibility to define how to determine the open price of 0DTE options to align more closely with realistic trading scenarios during backtesting.

2. Options Selection Based on Predefined Rules: 
Determine call and put strike prices using a systematic set of rules and calculations. For example, the call strike might be calculated as floor(SPY open price * 1.005) + 2.
 

## Configuration Parameters

### Dates
- `start_date`: Start date for backtesting, formatted as `yyyy-mm-dd`. 
- `end_date`: End date for backtesting, formatted as `yyyy-mm-dd`. 


### Portfolio and Weights Configuration
- `initial_portfolio_nominal_value`: Initial nominal value of the portfolio, which serves as the basis for calculating the NAV.
- `collateral_ratio`: The ratio of total assets deposited by fund investors to the initial portfolio nominal value. Any excess is utilized as cash. For example, with an `initial_portfolio_nominal_value` of $1,000,000 and a `collateral_ratio` of 1.3, investors are required to deposit $1,300,000, giving the portfolio an actual initial value of $1,300,000.
- `portfolio_weights_config`: Initial weights of each asset class within the portfolio at inception
At market open on `start_date`, the system will purchase an amount of equity (SPY ETF) equivalent to initial_portfolio_nominal_value * equity weight. The cash portion is reserved for supporting trading 0DTE options.

Note that, excluding cash, the weight of any other asset must not exceed 1, and the total sum of all asset weights must not surpass `collateral_ratio`. Non-compliance with these requirements will trigger a system error.


### Strategies Configuration

`strategy_selected`: Specifies which strategy to use, with options: 1 or 2.

`zero_cost_search_config`: Configurations for searching for a zero-cost collar in **Strategy 1**
- `upper_bound` and `lower_bound` define the upper and lower limits for the strike prices of options that we use to search for a zero-cost collar, based on the day's SPY open price. The upper limit is calculated as int(SPY_open_price * (1 + `upper_bound`)), and the lower limit as int(SPY_open_price * (1 + `lower_bound`)).

Example: If the SPY's open price on a given day is $500, with `upper_bound` = 0.01 and `lower_bound` = -0.02, the desired strike price range will be between 490 and 505, inclusive of all integers within this interval. The system will fetch the price data for both call and put options with strikes in this range to facilitate the search for a zero-cost collar.

Please note that absolute values of these bounds should be moderate. If they exceed 0.02—meaning the strike prices are distant from the day's SPY open price-it could result in getting a collar with call and put with poor liquidity. The price of such options would be around $0.01 or simulated by the system and it's not realistic to trade them. It also increases the volume of data the system needs to process.

`strike_selection_config`: Configurations for selecting call and put strike prices in **Strategy 2**
- `base_price`:         The base price type from which strike prices are calculated. Set to `'Open'`.
- `put_K_multiplier`:   Multiplier for put strike price before rounding. 
- `put_K_method`:       Rounding method for put strike price (options: 'floor' or 'ceil').
- `put_K_adjust`:       Adjustment to put strike price after rounding.
- `call_K_multiplier`:  Multiplier for call strike price before rounding.
- `call_K_method`:      Rounding method for call strike price (options: 'floor' or 'ceil').
- `call_K_adjust`:      Adjustment to call strike price after rounding.


### Option Parameters (Black-Scholes Model)
`bs_config`:
- `q`: Dividend yield of underlying asset. Set to `0` as the focus is solely on trading 0DTE options.
- `vol`: A constant volatility is used in the Black-Scholes Model. It is important to note that due to volatility skew/smirk, using a higher constant volatility can significantly underestimate the cost of collars and overestimate their payoff. The implied volatility of 0DTE options, with strike prices near the spot price, typically ranges from 8% to 15%.
- `r`: Assumed constant risk-free rate. Set to `0.05`.
- `time_to_expiration`: Time to expiration for the options. Set to `1/365` (one day).
- `spot_price_col`: Specifies the column from the underlying dataset that is used as the reference for the spot price. Set to 'open'.


### Option Open Price Configuration
`open_price_config` allows users of this project to specify how the open price of 0DTE options is determined during backtesting. This flexibility is essential for aligning the simulated trading conditions with more realistic trading scenarios that occur at market open.
- `bar_multiplier`: The size of the timespan of a bar (OHLCV).
- `bar_timespan`: Defines the unit of time for each data interval (options: second, minute, hour, day).
- `price_type`: Chooses the type of price to use (options: open, high, low, close, vwap). 'vwap' is calculated by dividing total dollar amount traded by total volume traded during a bar.
Example: If you set `bar_multiplier` to 3, `bar_timespan` to 'second', and `price_type` to 'vwap', the system will use the volume-weighted average price for the first 3 seconds after the market opens at 9:30 AM ET as the **open price** for a specific option during backtesting.

Please note: 
1. For options with low liquidity, such as those with strike prices far from the underlying spot price, there may be no transactions immediately after the market opens. Therefore, if you set `bar_multiplier` to 3, `bar_timespan` to 'second', and `price_type` to 'vwap', the API may not return any price data. In such cases, the system will automatically calculate a price using the Black-Scholes Model and assumptions in `bs_config`.

2. For options with low liquidity, setting `bar_multiplier` to 3, `bar_timespan` to 'minute', and `price_type` to 'open' might return the open price from the first 3-minute bar data available after market open. However, this open price may not occur near 9:30 AM ET, and significant price changes in SPY could have already taken place, which means that this price may not accurately represent a reliable approximation of the option's open price.


## Data
The primary data source for this project is currently the Polygon API. Additionally, we are actively exploring other reliable and stable databases or APIs to enhance our data accessibility and quality. 

If option price data is not available on Polygon.io at any point during backtesting, the Black-Scholes Model will be used to calculate price. In such cases, the system will print relevant information.

Cboe didn’t offer SPY 0DTE every day before Nov 17. 2022. If you backtest with 0DTE options before this date, it's likely that the requested option price is calculated using the Black-Scholes Model. Reference: https://cdn.cboe.com/resources/product_update/2022/Cboe-Options-to-List-SPY-and-QQQ-Tuesday-and-Thursday-Expiring-Weekly-Options.pdf  


## Findings
1. The smaller the range restricted by the 'lower_bound' and 'upper_bound' in 'zero_cost_search_config', the better the hedging effect.

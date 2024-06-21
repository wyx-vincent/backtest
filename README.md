# Backtest Framework for Multiple Investment Strategies


Innovative Money Market Fund (IMMF) 

The core object of this project is to investigate whether we can create a new form of money market fund, where the NAV never drops below $1.00 (specifically, never below $0.995), by holding SP500 ETFs (SPY) long-term, related short-term or long-term options (0DTE, LEAPS, etc.), as well as cash and cash equivalents (invested in traditional MMF). This fund can be used to track the value of U.S. dollars while providing investors with exposure to SP500. For the moment, we do not consider the requirements and restrictions of laws and regulations.

Current portfolio assumption: 
- Enter a collar using 0DTE, and let it expire at market close. 
- ETF dividends were not included in calculation
- No distribution/payout to fund investors
- Overnight SPY price changes are not hedged
- No transaction fees
- 0 interest rates in short selling and buying with leverage
- the code supports buying assets with leverage, but borrow limit has not been set.
- During short selling, the proceeds are deposited into a isolated margin account. When covering short positions, the margin is transferred to the cash account. Assume we are able to short when cash balance > required margin



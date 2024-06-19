# Backtest Framework for Multiple Investment Strategies


Innovative Money Market Fund (IMMF) 

The core object of this project is to investigate whether we can create a new form of money market fund, where the NAV never drops below $1.00 (specifically, never below $0.995), by holding SP500 ETFs (SPY) long-term, related short-term or long-term options (0DTE, LEAPS, etc.), as well as cash and cash equivalents (invested in traditional MMF). This fund can be used to track the value of U.S. dollars while providing investors with exposure to SP500. For the moment, we do not consider the requirements and restrictions of laws and regulations.

Current portfolio assumption: 
1) Only buy and hold one share of SPY at market open on the first day
2) Enter a collar strategy using 0DTE, and let it expire at market close. 
3) The costs of entering a collar strategy are negligible, as most of them are negative
4) ETF dividends were not included in calculation
5) No fund distribution/payout to fund investors
6) Overnight cost changes are not hedged

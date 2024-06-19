from portfolio import Portfolio
from backtest import Backtest
from strategies import *
from config import *
from utils import *
from data_processing import *


def main_function():

    # get data
    spy_df = get_spy_data()
    options_df = generate_option_chain(spy_df, time_to_expiration, generate_at='open')

    # instantiation
    my_portfolio = Portfolio(portfolio_initial_cash)
    my_portfolio.record_date(spy_df['Date'])
    my_strategy = ZeroCostCollar0DTE(spy_df, options_df)
    env = Backtest(my_portfolio, spy_df, options_df)

    # data cleaning and calculation
    env.main_df = my_strategy.select_and_update_options(env.main_df, selection_rules=strike_selection_config)
    env.update_option_price_at_close()
    env.main_df = my_strategy.update_collar_pnl(env.main_df)
    # plot_distribution(env.main_df['collar_profit'], x_label='Daily Collar Profit', title='Collar Profit Distribution')

    # need to rewrite the backtest process below
    env.update_values_temp_func()
    env.plot_nav_vs_spy()
    env.main_df.to_csv()

if __name__ == "__main__":
    main_function()



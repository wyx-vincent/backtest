import matplotlib.pyplot as plt

class Backtest:
    def __init__(self, portfolio, data, buy_leverage=1, sell_leverage=1):
        self.portfolio = portfolio
        self.buy_leverage = buy_leverage
        self.sell_leverage = sell_leverage
        self.issues = []

    def run():
        # record_date
        # loop date
            # execute strategy
            # update port_value
        pass

    def plot_nav_history(self, dates, portfolio_nav_list):
        # Plot NAV history
        plt.figure(figsize=(10, 6))
        plt.plot(dates, portfolio_nav_list, marker='o')
        plt.axhline(y=1, color='r', linestyle='--', label='$1 NAV')
        plt.xlabel('Date')
        plt.ylabel('Portfolio NAV')
        plt.title('Portfolio NAV History')
        plt.grid(True)
        plt.show()

    def get_issues(self):
        return self.issues



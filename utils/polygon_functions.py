from datetime import datetime, timedelta

import pandas as pd
from tqdm import tqdm
from polygon import RESTClient

class Option:

    api_key = ''
    client = RESTClient(api_key=api_key)

    def __init__(self, underlying_ticker, start_date, end_date):
        self.underlying_ticker = underlying_ticker
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        self.contracts = None
        self.trades = None
        self.bars = None
        self.quotes = None

    def get_contracts(self, contract_limit=1000):
        self.contracts = pd.DataFrame()
        as_of = self.start_date
        step = 5
        total_iterations = int((self.end_date - as_of).days / step) + 1
        with tqdm(total=total_iterations, desc="get contracts") as pbar:
            while as_of <= self.end_date:
                request = self.client.list_options_contracts(underlying_ticker=self.underlying_ticker, as_of=str(as_of),
                                                             expired=False, limit=contract_limit, raw=False)
                data = pd.DataFrame.from_records([vars(c) for c in request])
                self.contracts = pd.concat([self.contracts, data])
                self.contracts = self.contracts.drop_duplicates(subset=['ticker'])
                as_of += timedelta(days=step)
                pbar.update(1)
        self.contracts = self.contracts.reset_index(drop=True)

    def get_trades(self, contract_id, trade_limit=50000):
        request = self.client.list_trades(ticker=contract_id, timestamp_gte=str(self.start_date),
                                          timestamp_lte=str(self.end_date), limit=trade_limit, sort='timestamp',
                                          order='asc', raw=False)
        self.trades = [vars(t) for t in request]

    def get_quotes(self, contract_id, quote_limit=50000):
        request = self.client.list_quotes(ticker=contract_id, timestamp_gte=str(self.start_date),
                                          timestamp_lte=str(self.end_date), limit=quote_limit, sort='timestamp',
                                          order='asc', raw=False)
        self.quotes = [vars(q) for q in request]

    def get_bars(self, contract_id, multiplier, freq, bar_limit=50000, adjusted=False):
        request = self.client.list_aggs(ticker=contract_id, multiplier=multiplier, timespan=freq,
                                        from_=str(self.start_date), to=str(self.end_date), adjusted=adjusted,
                                        sort='asc', limit=bar_limit, raw=False)
        self.bars = [vars(b) for b in request]


class Stock:

    api_key = ''
    client = RESTClient(api_key=api_key)

    def __init__(self, underlying_ticker, start_date, end_date):
        self.underlying_ticker = underlying_ticker
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        self.trades = None
        self.bars = None

    def get_trades(self, trade_limit=50000):
        request = self.client.list_trades(ticker=self.underlying_ticker, timestamp_gte=str(self.start_date),
                                          timestamp_lte=str(self.end_date), limit=trade_limit, sort='timestamp',
                                          order='asc', raw=False)
        self.trades = [vars(t) for t in request]

    def get_bars(self, multiplier, freq, bar_limit=50000, adjusted=False):
        request = self.client.list_aggs(ticker=self.underlying_ticker, multiplier=multiplier, timespan=freq,
                                        from_=str(self.start_date), to=str(self.end_date), adjusted=adjusted,
                                        sort='asc', limit=bar_limit, raw=False)
        self.bars = [vars(b) for b in request]

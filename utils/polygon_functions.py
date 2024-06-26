import concurrent.futures

import numpy as np
from polygon import RESTClient
from tqdm import tqdm

from utils import blackscholes_price


class DataNotAvailableError(Exception):
    """Exception raised when the required data is not available from the API."""
    pass


class PolygonAPI():
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = RESTClient(api_key)


    def fetch_option_price(self, ticker, multiplier, timespan, date_from, date_to, price_type, raise_error=True):
        if price_type not in ['open', 'high', 'low', 'close', 'vwap']:
            raise ValueError("price type input is wrong, please use one of ['open', 'high', 'low', 'close', 'vwap']. ")
        
        request = self.client.list_aggs(ticker, multiplier, timespan, from_=date_from, to=date_to)
        bars = [b for b in request]

        if bars:
            return getattr(bars[0], price_type)
        elif raise_error:
            error = (f"No data available or unsuccessful API request. "
                    f"option ticker: {ticker}, multiplier: {multiplier}, timespan: {timespan}, from: {date_from}, to: {date_to}. ")
            raise DataNotAvailableError(error)
        else:
            return None


    def try_get_polygon_price(self, option_ticker, bar_multiplier, bar_timespan, date_from, date_to, price_type, option_type, spot_price, strike, bs_config, bs_days):
        try:
            return self.fetch_option_price(
                option_ticker,
                bar_multiplier, 
                bar_timespan, 
                date_from, 
                date_to, 
                price_type
            )
        
        except DataNotAvailableError:
            bs_days.append(f"{date_from} for {option_type}, K={strike}")
            return blackscholes_price(
                K=strike,
                S=spot_price,
                T=bs_config['time_to_expiration'],
                vol=bs_config['vol'],
                r=bs_config['r'],
                q=bs_config['q'],
                callput=option_type
            )


    def try_get_polygon_price_multithread(self, option_data_df, bar_multiplier, bar_timespan, price_type, bs_config):
        option_data_df['open_price'] = np.nan
        prices = {}
        bs_days = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_option = {
                executor.submit(self.fetch_option_price, row['option_tickers'], bar_multiplier, bar_timespan, row['date_from'], 
                                row['date_to'], price_type, raise_error=False): index for index, row in option_data_df.iterrows()
            }

            futures = concurrent.futures.as_completed(future_to_option)
            futures = tqdm(futures, total=len(future_to_option), desc="Fetching option prices using multithreading")

            for future in futures:
                index = future_to_option[future]
                row = option_data_df.iloc[index]
                price = future.result()
                if price is None:
                    # No price data available, use Black-Scholes model
                    bs_days.append(f"{row['date_from']} for K={row['strike']} {row['option_type']} ")
                    price = blackscholes_price(
                        K=row['strike'],
                        S=row['spot_price'],
                        T=bs_config['time_to_expiration'],
                        vol=bs_config['vol'],
                        r=bs_config['r'],
                        q=bs_config['q'],
                        callput=row['option_type']
                    )
                prices[index] = price
        
        for index, price in prices.items():
            option_data_df.at[index, 'open_price'] = price

        return option_data_df, bs_days




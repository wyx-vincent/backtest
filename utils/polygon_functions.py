from datetime import datetime, timedelta

from polygon import RESTClient


class DataNotAvailableError(Exception):
    """Exception raised when the required data is not available from the API."""
    pass


def get_0DTE_price_at_open(underlying_ticker: str, option_type: str, strike: float, date: str, bar_multiplier: int=3, bar_timespan: str='second', price_type: str='vwap'):
    
    """
    Retrieve the price of a 0DTE (Zero Days to Expiration) option at market open using the Polygon.io API.

    Parameters
    ----------
    underlying_ticker : str
        The ticker of the underlying asset for the option.
    
    option_type : str
        The type of option, either 'call' or 'put'.
    
    strike : float
        The strike price of the option.
    
    date : str
        The date for which the option price is queried, in the format 'yyyy-mm-dd'. This is also the expiration date of the 0DTE option.
    
    bar_multiplier : int, optional
        The duration of each bar in seconds. This defines the time span for the aggregated bar data. Default is 3 seconds.
    
    bar_timespan : str, optionl
        The time span of a bar data, Possible values are second, minute, hour, day

    price_type : str, optional
        The price type used to determine the market ”opening price“. Possible values are 'open', 'high', 'low', 'close', and 'vwap'. Default is 'vwap'.
        'vwap' is the volume weighted average price, calculated by dividing the total dollar amount traded by the total volume traded during a bar.

    Returns
    -------
    float
        The price of the specified option at market open.

    Example
    -------
    If `bar_multiplier` is set to 3 and `price_type` is 'vwap', the function will return the volume weighted average price within the first 3 seconds after the market opens at 9:30 AM ET.
    """

    if option_type not in ['call', 'put']:
        raise ValueError("option type input is wrong, please use either 'call' or 'put'. ")
    
    if price_type not in ['open', 'high', 'low', 'close', 'vwap']:
        raise ValueError("price type input is wrong, please use one of ['open', 'high', 'low', 'close', 'vwap']. ")

    
    api_key = 'MPkBRXXyfleZXSJQp8_bOsKuqo2Wi_Gk'
    client = RESTClient(api_key=api_key)

    underlying_ticker_str = underlying_ticker.upper()
    date_str = date.replace('-', '')[2:]
    type_str = option_type[0].upper()
    strike_str = f"{int(strike*1000):08d}"
    ticker = 'O:' + underlying_ticker_str + date_str + type_str + strike_str
    
    # date_obj = datetime.strptime(date, '%Y-%m-%d')
    # market_open_dt = date_obj + timedelta(hours=9, minutes=30)
    # bar_begin_time = int(market_open_dt.timestamp() * 1000)      # ms timestamp, do not use timestamp to request data from polygon.io, it's not stable
    request = client.list_aggs(ticker, multiplier=bar_multiplier, timespan='second', from_=date, to=date)
    bars = [b for b in request]
    if len(bars) == 0:
        error = (f"No data available or unsuccessful API request. "
                 f"option ticker: {ticker}, multiplier: {bar_multiplier}, timespan: 'second', from: {date}, to: {date}. ")
        raise DataNotAvailableError(error)
    
    price = getattr(bars[0], price_type)
    # print(ticker, price)
    
    return price



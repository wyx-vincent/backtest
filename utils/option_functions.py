
import numpy as np
from scipy.stats import norm



# Black-Scholes Option Pricing
def blackscholes_price(K, T, S, vol, r=0, q=0, callput='call'):
    """Compute the call/put option price in the Black-Scholes model
    
    Parameters
    ----------
    K: scalar or array_like
        The strike of the option.
    T: scalar or array_like
        The maturity of the option, expressed in years (e.g. 0.25 for 3-month and 2 for 2 years)
    S: scalar or array_like
        The current price of the underlying asset.
    vol: scalar or array_like
        The implied Black-Scholes volatility.
    r: scalar or array_like
        The annualized risk-free interest rate, continuously compounded.
    q: scalar or array_like
        The annualized continuous dividend yield.
    callput: str
        Must be either 'call' or 'put'.

    Returns
    -------
    price: scalar or array_like
        The price of the option.

    Examples
    --------
    >>> blackscholes_price(95, 0.25, 100, 0.2, r=0.05, callput='put')
    1.5342604771222823
    """
    F = S*np.exp((r-q)*T)
    v = vol*np.sqrt(T)
    d1 = np.log(F/K)/v + 0.5*v
    d2 = d1 - v
    try:
        opttype = {'call':1, 'put':-1}[callput.lower()]
    except:
        raise ValueError('The value of callput must be either "call" or "put".')
    price = opttype*(F*norm.cdf(opttype*d1)-K*norm.cdf(opttype*d2))*np.exp(-r*T)
    return price



# Monte Carlo Simulation in the Black-Scholes Model
def blackscholes_mc(S=100, vol=0.2, r=0, q=0, ts=np.linspace(0, 1, 13), npaths=10):
    """Generate Monte-Carlo paths in Black-Scholes model.

    Parameters
    ----------
    S: scalar
        The spot price of the underlying security.
    vol: scalar
        The implied Black-Scholes volatility.
    r: scalar
        The annualized risk-free interest rate, continuously compounded.
    q: scalar
        The annualized continuous dividend yield.
    ts: array_like
        The time steps of the simualtion
    npaths: int
        the number of paths to simulate

    Returns
    -------
    paths: ndarray
        The Monte-Carlo paths.
    """
    nsteps = len(ts) - 1
    ts = np.asfarray(ts)[:, np.newaxis]
    W = np.cumsum(np.vstack((np.zeros((1, npaths), dtype=np.float64),
                             np.random.randn(nsteps, npaths) * np.sqrt(np.diff(ts, axis=0)))),
                  axis=0)
    paths = np.exp(-0.5*vol**2*ts + vol*W)*S*np.exp((r-q)*ts)
    return paths



# Black-Scholes Implied Volatility
# all inputs must be scalar
def blackscholes_impv_scalar(K, T, S, value, r=0, q=0, callput='call', tol=1e-6, maxiter=500):
    """Compute implied vol in Black-Scholes model
    
    Parameters
    ----------
    K: scalar
        The strike of the option.
    T: scalar
        The maturity of the option.
    S: scalar
        The current price of the underlying asset.
    value: scalar
        The value of the option
    callput: str
        Must be either 'call' or 'put'

    Returns
    -------
    vol: scalar
        The implied vol of the option.
    """
    if (K <= 0) or (T <= 0) or (S <= 0):
        return np.nan
    F = S*np.exp((r-q)*T)
    K = K/F
    value = value*np.exp(r*T)/F
    try:
        opttype = {'call':1, 'put':-1}[callput.lower()]
    except:
        raise ValueError('The value of callput must be either "call" or "put".')
    # compute the time-value of the option
    value -= max(opttype * (1 - K), 0)
    if value < 0:
        return np.nan
    if (value == 0):
        return 0
    j = 1
    p = np.log(K)
    if K >= 1:
        x0 = np.sqrt(2 * p)
        x1 = x0 - (0.5 - K * norm.cdf(-x0) - value) * np.sqrt(2*np.pi)
        while (abs(x0 - x1) > tol*np.sqrt(T)) and (j < maxiter):
            x0 = x1
            d1 = -p/x1+0.5*x1
            x1 = x1 - (norm.cdf(d1) - K*norm.cdf(d1-x1)-value)*np.sqrt(2*np.pi)*np.exp(0.5*d1**2)
            j += 1
        return x1 / np.sqrt(T)
    else:
        x0 = np.sqrt(-2 * p)
        x1 = x0 - (0.5*K-norm.cdf(-x0)-value)*np.sqrt(2*np.pi)/K
        while (abs(x0-x1) > tol*np.sqrt(T)) and (j < maxiter):
            x0 = x1
            d1 = -p/x1+0.5*x1
            x1 = x1-(K*norm.cdf(x1-d1)-norm.cdf(-d1)-value)*np.sqrt(2*np.pi)*np.exp(0.5*d1**2)
            j += 1
        return x1 / np.sqrt(T)

# vectorized version
blackscholes_impv = np.vectorize(blackscholes_impv_scalar, excluded={'callput', 'tol', 'maxiter'})



if __name__ == '__main__':

    # exmaples

    # Compute the prices of European put options with a matrix of expiries and strikes, using numpy's broadcasting feature
    Ks = np.array([90, 100, 110])
    Ts = np.array([0.25, 0.5, 1])
    price_matrix = blackscholes_price(Ks, Ts[:, np.newaxis], S=100, vol=0.2, r=0.05, q=0.02, callput='put')
    print('price matrix')
    print(price_matrix)
    print('')

    # Compute the implied volatility of European put options with a matrix of expiries and strikes, using numpy's broadcasting feature
    implied_vol = blackscholes_impv(Ks, Ts, S=100, value=10.5, callput='put')
    print('implied volatility', implied_vol)
    print('')

    # Compare the results from Black-Scholes formulas and Monte Carlo simulation
    S = 100
    vol = 0.2
    r = 0.05
    q = 0.02
    K = 95
    T = 0.5

    # Black-Scholes formulas
    c_bs_price = blackscholes_price(K, T, S, vol, r, q, callput='call')
    p_bs_price = blackscholes_price(K, T, S, vol, r, q, callput='put')

    # Monte Carlo simulation
    npaths = 10000
    ts = np.linspace(0, T, int(round(T*252))+1) # use 'int(round(T*252))+1' for daily timestep, 13 for monthly timestep

    # plot simulated paths
    '''
    import matplotlib.pyplot as plt
    paths = blackscholes_mc(S, vol, r, q, ts=ts, npaths=npaths)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(ts, paths[:, :50])
    ax.set_xticks(ts)
    ax.set_xticklabels(['0', '1M', '2M', '3M', '4M', '5M', '6M', '7M', '8M', '9M', '10M', '11M', '1Y'])
    ax.set_ylabel('Stock Price')
    ax.grid(True)
    plt.show()
    '''

    c_mc_price_lst = []
    p_mc_price_lst = []

    for _ in range(50):
        paths = blackscholes_mc(S, vol, r, q, ts=ts, npaths=npaths)
        c_mc_price_lst.append(np.mean(np.maximum(paths[-1]-K, 0))*np.exp(-r*T))
        p_mc_price_lst.append(np.mean(np.maximum(K-paths[-1], 0))*np.exp(-r*T))

    print('European call price using Black-Scholes', c_bs_price)
    print('European call price using Monte Carlo Simulation', np.mean(c_mc_price_lst))
    print('')
    print('European put price using Black-Scholes', p_bs_price)
    print('European put price using Monte Carlo Simulation', np.mean(p_mc_price_lst))
    print('')



"""Signals at close t; the execution engine applies the time lag."""
import numpy as np
import pandas as pd

def signals(p, ma=200, vol_window=60, target_vol=.10, mode='combined', mr_window=20, mr_entry=1.5):
    if ma < 2 or vol_window < 2 or mr_window < 2 or target_vol <= 0 or mr_entry <= 0:
        raise ValueError('Invalid strategy parameters')
    r = p.pct_change(fill_method=None)
    vol = r.rolling(vol_window).std(ddof=1)*np.sqrt(252)
    trend = (p > p.rolling(ma).mean()).astype(float)
    scale = (target_vol/vol.clip(lower=.01)).clip(upper=1)
    if mode == 'combined': s = trend*scale
    elif mode == 'trend': s = trend
    elif mode == 'vol': s = scale
    elif mode == 'buy_hold': s = pd.Series(1., index=p.index)
    elif mode == 'fixed_50': s = pd.Series(.5, index=p.index)
    elif mode == 'mean_reversion':
        # Stateless monthly oversold allocation. Not a daily stop/limit strategy.
        mean = p.rolling(mr_window).mean()
        sd = p.rolling(mr_window).std(ddof=1)
        z = (p-mean)/sd.replace(0,np.nan)
        s = (z < -mr_entry).astype(float)
    else: raise ValueError(mode)
    warmup = max(ma,vol_window+1,mr_window)
    if mode not in ('buy_hold','fixed_50'):
        s = s.where(p.rolling(warmup).count() >= warmup)
    return s.rename('signal')

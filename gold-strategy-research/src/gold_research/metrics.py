"""Historical descriptive metrics; Sharpe assumes zero risk-free rate."""
import numpy as np

def metrics(d):
    if len(d) < 2: raise ValueError('Need at least two return observations')
    r=d['return']; n=len(r); growth=(1+r).prod()
    curve=np.r_[1., (1+r).cumprod().to_numpy()]
    dd=curve/np.maximum.accumulate(curve)-1
    sd=r.std(ddof=1)
    return {'CAGR':growth**(252/n)-1,'Volatility':sd*np.sqrt(252),
            'Sharpe_RF0':r.mean()/sd*np.sqrt(252) if sd>0 else np.nan,
            'MaxDrawdown':dd.min(),'TotalReturn':growth-1,
            'AvgWeight':d.weight.mean(),'TurnoverAnnual':d.turnover.sum()*252/n}

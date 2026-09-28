"""Exploratory paired circular block bootstrap; not a profitability proof."""
import numpy as np

def paired_block_interval(strategy,benchmark,block_size=20,repetitions=2000,seed=42):
    pair=strategy.align(benchmark,join='inner')
    x=(pair[0]-pair[1]).dropna().to_numpy()
    if len(x)<2*block_size: raise ValueError('Insufficient observations for block bootstrap')
    rng=np.random.default_rng(seed);n=len(x);means=[]
    for _ in range(repetitions):
        starts=rng.integers(0,n,size=int(np.ceil(n/block_size)))
        ix=((starts[:,None]+np.arange(block_size))%n).ravel()[:n]
        means.append(x[ix].mean()*252)
    lo,hi=np.quantile(means,[.025,.975])
    return {'annualized_mean_daily_difference':x.mean()*252,'lower_95':lo,'upper_95':hi,
            'block_size':block_size,'repetitions':repetitions,'seed':seed,
            'note':'Exploratory stationary-block assumption; annualized arithmetic mean difference, NOT CAGR difference. No multiple-testing correction.'}

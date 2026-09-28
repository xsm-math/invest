"""Annual rolling selection. Training only uses data known at the cutoff."""
import itertools
import numpy as np
import pandas as pd
from .engine import backtest
from .metrics import metrics
from .strategies import signals


def select_parameters(p, test_year, config):
    wf = config['walk_forward']
    cutoff = pd.Timestamp(f'{test_year}-01-01')
    train_start = pd.Timestamp(f"{test_year-wf['train_years']}-01-01")
    history = p.loc[p.index < cutoff]
    if history.empty or (history.index >= train_start).sum() < 252:
        raise ValueError('Insufficient training history')
    candidates=[]
    for ma, target in itertools.product(wf['ma_grid'],wf['vol_grid']):
        s=signals(history,ma=ma,target_vol=target,vol_window=config['vol_window'])
        d=backtest(history,s,start=train_start,cost_bps=config['cost_bps'],cash_rate=config['cash_rate'])
        score=metrics(d)['Sharpe_RF0']
        candidates.append({'test_year':test_year,'train_start':str(d.index[0].date()),
                           'train_end':str(d.index[-1].date()),'ma':ma,'target_vol':target,'train_sharpe':score})
    scores=pd.DataFrame(candidates)
    finite=scores[np.isfinite(scores.train_sharpe)]
    if finite.empty: raise ValueError('No finite training score; refusing an implicit fallback')
    # Explicit stable tie break: Sharpe desc, MA asc, target volatility asc.
    selected=finite.sort_values(['train_sharpe','ma','target_vol'],ascending=[False,True,True]).iloc[0].to_dict()
    return selected,scores


def walk_forward(p,config):
    wf=config['walk_forward']; start=wf['first_test_year']; last=wf['last_test_year']
    target=pd.Series(0.,index=p.index,name='signal')
    # Map signal-date to its next execution-date year. December's final signal
    # must use the NEW year's selected parameters, not the previous year's.
    next_year=pd.Series(np.r_[p.index.year[1:],-1],index=p.index)
    folds=[];all_scores=[]
    for year in range(start,last+1):
        selected,scores=select_parameters(p,year,config)
        s=signals(p,ma=int(selected['ma']),target_vol=float(selected['target_vol']),
                  vol_window=config['vol_window'])
        mask=next_year==year
        if not mask.any(): raise ValueError(f'No test dates for {year}')
        target.loc[mask]=s.loc[mask]
        selected['selected_on']=selected['train_end']
        folds.append(selected);all_scores.append(scores)
    d=backtest(p.loc[p.index < f'{last+1}-01-01'],target,start=f'{start}-01-01',
               cost_bps=config['cost_bps'],cash_rate=config['cash_rate'])
    for fold in folds:
        sub=d[d.index.year==int(fold['test_year'])]
        fold.update({'test_start':str(sub.index[0].date()),'test_end':str(sub.index[-1].date()),
                     **{'test_'+k:v for k,v in metrics(sub).items()}})
    return d,pd.DataFrame(folds),pd.concat(all_scores,ignore_index=True)

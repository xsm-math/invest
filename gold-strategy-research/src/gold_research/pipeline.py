"""Reproducible research pipeline. All reports are derived from actual runs."""
from pathlib import Path
import hashlib,json,platform
import numpy as np
import pandas as pd
import matplotlib
from .data import load_prices
from .engine import backtest
from .strategies import signals
from .metrics import metrics
from .walkforward import walk_forward
from .uncertainty import paired_block_interval
from .reporting import plot,write_report


def run(config,out):
    cfg=dict(config);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'trades').mkdir(exist_ok=True);(out/'daily').mkdir(exist_ok=True)
    path=Path(cfg['data_path']);p=load_prices(path);p=p.loc[p.index<cfg['end_exclusive']]
    if p.index.min()>pd.Timestamp('2005-01-31') or p.index.max()<pd.Timestamp('2025-12-24'):
        raise ValueError('Default study requires full 2005-2025 history; adjust study design before using a shorter dataset')
    def signal(mode,**kw):
        params=dict(ma=cfg['ma'],vol_window=cfg['vol_window'],target_vol=cfg['target_vol'],
                    mr_window=cfg['mr_window'],mr_entry=cfg['mr_entry']);params.update(kw)
        return signals(p,mode=mode,**params)
    def simulate(s,start=cfg['start'],buy_hold=False,cost=cfg['cost_bps']):
        return backtest(p,s,start=start,cost_bps=cost,cash_rate=cfg['cash_rate'],buy_hold=buy_hold)
    def save(d,name):
        d.to_csv(out/'daily'/f'{name}.csv')
        trades=d[d.trade_value.abs()>1e-12].copy()
        trades['side']=np.where(trades.trade_value>0,'BUY','SELL')
        trades.to_csv(out/'trades'/f'{name}.csv')
    results={};rows=[]
    modes=['buy_hold','fixed_50','trend','vol','combined','mean_reversion']
    for mode in modes:
        d=simulate(signal(mode),buy_hold=mode=='buy_hold');results[mode]=d;save(d,mode)
        for name,lo,hi in [('All',cfg['start'],cfg['end_exclusive']),('2007-2014','2007','2015'),('2015-2019','2015','2020'),('2020-2025','2020','2026')]:
            sub=d[(d.index>=lo)&(d.index<hi)]
            rows.append({'Strategy':mode,'Period':name,**metrics(sub)})
    summary=pd.DataFrame(rows);summary.to_csv(out/'metrics.csv',index=False)
    annual=pd.DataFrame({mode:d['return'].groupby(d.index.year).apply(lambda x:(1+x).prod()-1) for mode,d in results.items()})
    annual.to_csv(out/'annual_returns.csv')
    d,folds,scores=walk_forward(p,cfg);save(d,'walk_forward')
    folds.to_csv(out/'walk_forward_folds.csv',index=False);scores.to_csv(out/'training_candidates.csv',index=False)
    wf_results={'walk_forward':d}
    start=f"{cfg['walk_forward']['first_test_year']}-01-01"
    for mode in ['buy_hold','fixed_50','combined']:
        base=simulate(signal(mode),start=start,buy_hold=mode=='buy_hold')
        # Evaluation end is the same as the stitched walk-forward account.
        base=base.loc[:d.index[-1]];wf_results[mode]=base;save(base,'wf_benchmark_'+mode)
    wf_summary=pd.DataFrame([{'Strategy':mode,**metrics(v)} for mode,v in wf_results.items()])
    wf_summary.to_csv(out/'walk_forward_comparison.csv',index=False)
    boot=paired_block_interval(d['return'],wf_results['fixed_50']['return'],**cfg['bootstrap'])
    (out/'uncertainty.json').write_text(json.dumps(boot,indent=2),encoding='utf-8')
    sensitivity=[]
    for ma in cfg['walk_forward']['ma_grid']:
        for vol in cfg['walk_forward']['vol_grid']:
            x=simulate(signal('combined',ma=ma,target_vol=vol))
            sensitivity.append({'MA':ma,'TargetVol':vol,**metrics(x.loc['2020':'2025'])})
    pd.DataFrame(sensitivity).to_csv(out/'sensitivity_POSTHOC.csv',index=False)
    costs=[]
    for cost in [0,5,10,20,50]:
        x=simulate(signal('combined'),cost=cost)
        costs.append({'CostBps':cost,**metrics(x.loc['2020':'2025'])})
    pd.DataFrame(costs).to_csv(out/'cost_sensitivity.csv',index=False)
    plot(results,out/'fixed_strategies.png','GLD | Fixed rules | Monthly close execution')
    plot(wf_results,out/'walk_forward.png','GLD | Rolling 5-year selection, next-year evaluation')
    sha=hashlib.sha256(path.read_bytes()).hexdigest()
    manifest={'config':cfg,'data_sha256':sha,'python':platform.python_version(),
              'numpy':np.__version__,'pandas':pd.__version__,'matplotlib':matplotlib.__version__,
              'first_price':str(p.index.min().date()),'last_price':str(p.index.max().date()),'rows':len(p),
              'note':'Historical research; no genuinely untouched prospective test. Raw market data excluded from Git.'}
    (out/'run_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    write_report(out,summary,wf_summary,folds,boot,cfg,sha)
    print(wf_summary.to_string(index=False));print(f'Report: {out / "REPORT.md"}')
    return summary,wf_summary

"""Self-financing close-to-close account with proportional transaction costs."""
import numpy as np
import pandas as pd

def backtest(p, s, start='2007-01-01', cost_bps=10., cash_rate=0., buy_hold=False):
    """At close t, execute signal t-1 on first observed trading day of month.
    Carry previous shares through t's close; then charge exact proportional cost.
    Weight is fraction of AFTER-cost NAV, solved analytically (includes drift).
    """
    if not np.isfinite([cost_bps,cash_rate]).all() or not 0 <= cost_bps < 10000 or cash_rate <= -1:
        raise ValueError('Invalid costs/rate')
    decision = s.reindex(p.index).shift(1)
    active = p.index >= pd.Timestamp(start)
    if active.sum() < 2 or decision.loc[active].isna().any():
        raise ValueError('Insufficient warmup or missing signal; provide earlier data')
    dates = p.index[active]
    cash, shares, prev_nav, prev_date = 1., 0., 1., None
    rows=[]; c=cost_bps/10000
    for date in dates:
        price=float(p.loc[date]); previous_shares=shares
        if prev_date is not None:
            cash *= (1+cash_rate)**((date-prev_date).days/365.25)
        asset=shares*price; pre_nav=cash+asset
        rebalance = prev_date is None or (not buy_hold and date.to_period('M') != prev_date.to_period('M'))
        trade=fee=0.; target=np.nan
        if rebalance:
            target=float(decision.loc[date])
            if not 0 <= target <= 1: raise ValueError('Target outside [0,1]')
            if target*pre_nav >= asset:
                new_asset=target*(pre_nav+c*asset)/(1+target*c)
            else:
                new_asset=target*(pre_nav-c*asset)/(1-target*c)
            trade=new_asset-asset; fee=c*abs(trade)
            cash=pre_nav-new_asset-fee; shares=new_asset/price
        nav=cash+shares*price
        rows.append([date,nav,nav/prev_nav-1,shares*price/nav,decision.loc[date],target,
                     abs(trade)/pre_nav,fee,shares,previous_shares,cash,trade,price,pre_nav])
        prev_nav=nav; prev_date=date
    return pd.DataFrame(rows, columns=['Date','nav','return','weight','available_signal','target',
                'turnover','fee','shares','prior_shares','cash','trade_value','price','pre_trade_nav']).set_index('Date')

import unittest
import numpy as np
import pandas as pd
from gold_research.strategies import signals
from gold_research.engine import backtest

class AccountingAndCausality(unittest.TestCase):
    def setUp(self):
        self.idx=pd.bdate_range('2005-01-03',periods=1000)
        self.p=pd.Series(100*np.exp(np.arange(1000)*.0004+.01*np.sin(np.arange(1000)/7)),index=self.idx)
    def test_future_prices_cannot_change_past(self):
        altered=self.p.copy();altered.iloc[800:]*=1.4
        a=backtest(self.p,signals(self.p));b=backtest(altered,signals(altered))
        pd.testing.assert_frame_equal(a.loc[:self.idx[799]],b.loc[:self.idx[799]])
    def test_same_day_signal_not_traded(self):
        a=signals(self.p);b=a.copy()
        d=backtest(self.p,a); date=d.index[0];b.loc[date]=0
        x=backtest(self.p,b)
        self.assertAlmostEqual(d.loc[date,'nav'],x.loc[date,'nav'])
        self.assertAlmostEqual(d.loc[date,'shares'],x.loc[date,'shares'])
    def test_buy_hold_and_entry_fee(self):
        s=pd.Series(1.,index=self.idx)
        d=backtest(self.p,s,cost_bps=10,buy_hold=True)
        expected=self.p.loc[d.index]/self.p.loc[d.index[0]]/1.001
        np.testing.assert_allclose(d.nav,expected,rtol=1e-12)
        self.assertEqual((d.turnover>0).sum(),1)
    def test_rebalance_target_after_cost(self):
        s=pd.Series(.5,index=self.idx)
        d=backtest(self.p,s,cost_bps=10)
        trade=d.target.notna()
        np.testing.assert_allclose(d.loc[trade,'weight'],.5,atol=1e-12)
        self.assertTrue((d.cash>=-1e-12).all())
        self.assertTrue((d.loc[trade,'turnover'].iloc[1:]>0).any())
    def test_cash_only(self):
        s=pd.Series(0.,index=self.idx)
        d=backtest(self.p,s)
        np.testing.assert_allclose(d.nav,1)
        self.assertEqual(d.fee.sum(),0)

if __name__=='__main__':unittest.main(verbosity=2)

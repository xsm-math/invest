import copy
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from gold_research.strategies import signals
from gold_research.engine import backtest
from gold_research.walkforward import walk_forward,select_parameters
from gold_research.uncertainty import paired_block_interval
from gold_research.data import load_prices
from pathlib import Path
import tempfile

class ResearchTests(unittest.TestCase):
    def setUp(self):
        idx=pd.bdate_range('2005-01-03','2017-12-29')
        rng=np.random.default_rng(123)
        self.p=pd.Series(100*np.exp(np.cumsum(rng.normal(.0003,.009,len(idx)))),index=idx)
        self.cfg={'vol_window':60,'cost_bps':10.,'cash_rate':0.,'walk_forward':{
            'train_years':5,'first_test_year':2015,'last_test_year':2017,
            'ma_grid':[150,200],'vol_grid':[.10]}}
    def test_future_shock_cannot_change_selection(self):
        a,scores=select_parameters(self.p,2015,self.cfg)
        changed=self.p.copy();changed.loc['2015':]*=2
        b,new_scores=select_parameters(changed,2015,self.cfg)
        self.assertEqual(a,b);pd.testing.assert_frame_equal(scores,new_scores)
        self.assertLess(pd.Timestamp(a['train_end']),pd.Timestamp('2015-01-01'))
    def test_single_candidate_stitch_equals_continuous_fixed_strategy(self):
        cfg=copy.deepcopy(self.cfg);cfg['walk_forward']['ma_grid']=[200]
        d,folds,_=walk_forward(self.p,cfg)
        fixed=backtest(self.p,signals(self.p),start='2015-01-01')
        pd.testing.assert_frame_equal(d,fixed)
        self.assertEqual(len(folds),3)
    def test_new_year_first_trade_uses_new_parameters(self):
        def select(p,year,cfg):
            row={'test_year':year,'train_start':f'{year-5}-01-03',
                 'train_end':str(p[p.index<f'{year}-01-01'].index[-1].date()),
                 'ma':150 if year==2015 else 200,'target_vol':.08 if year==2015 else .12,'train_sharpe':.5}
            return row,pd.DataFrame([row])
        with patch('gold_research.walkforward.select_parameters',side_effect=select):
            d,_,_=walk_forward(self.p,self.cfg)
        date=d.loc['2016'].index[0];prev=self.p.index[self.p.index.get_loc(date)-1]
        expected=signals(self.p,ma=200,target_vol=.12).loc[prev]
        self.assertAlmostEqual(d.loc[date,'target'],expected)
    def test_identical_pair_has_zero_interval(self):
        x=self.p.pct_change().dropna()
        out=paired_block_interval(x,x,repetitions=50)
        self.assertEqual(out['lower_95'],0);self.assertEqual(out['upper_95'],0)
    def test_data_rejects_duplicate_dates(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'prices.csv';p.write_text('Date,AdjClose\n2020-01-01,100\n2020-01-01,101\n')
            with self.assertRaisesRegex(ValueError,'unique'):load_prices(p)
    def test_long_only_and_warmup(self):
        for mode in ['combined','trend','vol','mean_reversion']:
            s=signals(self.p,mode=mode)
            self.assertTrue(s.iloc[:199].isna().all())
            self.assertTrue(s.dropna().between(0,1).all())

if __name__=='__main__':unittest.main()

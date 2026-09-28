"""English research figures and a short figure index."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

MODES=['buy_hold','trend','vol','combined','fixed_50']
NAMES=['Buy and hold','Trend timing','Volatility targeting','Combined','Fixed 50%']
COLORS=['#64748b','#dd8730','#007f91','#a05ba6','#528a47']


def explain(out,summary,results=None,font=None):
    # font is retained for compatibility; figures now use English labels.
    out=Path(out)
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':10,
                         'axes.spines.top':False,'axes.spines.right':False}):
        fig,axes=plt.subplots(2,3,figsize=(14,8))
        fields=['CAGR','Volatility','MaxDrawdown']
        titles=['Annualized return (%)','Annualized volatility (%)','Maximum drawdown (%)']
        for row,period in enumerate(['All','2020-2025']):
            d=summary[summary.Period==period].set_index('Strategy').loc[MODES]
            for col,key in enumerate(fields):
                ax=axes[row,col]
                vals=(d[key].abs() if key=='MaxDrawdown' else d[key])*100
                all_vals=summary[summary.Strategy.isin(MODES)&summary.Period.isin(['All','2020-2025'])][key]
                all_vals=(all_vals.abs() if key=='MaxDrawdown' else all_vals)*100
                ax.barh(range(5),vals,color=COLORS,height=.55)
                ax.set_yticks(range(5),NAMES if col==0 else ['']*5);ax.invert_yaxis()
                ax.set_xlim(min(0,all_vals.min()*1.2),max(1,all_vals.max()*1.22))
                for i,v in enumerate(vals):ax.text(v+.25,i,f'{v:.2f}',va='center')
                ax.xaxis.grid(True,alpha=.15);ax.set_axisbelow(True)
                if row==0:ax.set_title(titles[col],pad=12)
            axes[row,0].set_ylabel('2007–2025' if row==0 else '2020–2025',labelpad=15)
        fig.tight_layout();fig.savefig(out/'plain_comparison.png',dpi=150);plt.close(fig)
        if results is not None:
            fig,axes=plt.subplots(2,1,figsize=(11,8),sharex=True)
            for mode,name,color in zip(MODES,NAMES,COLORS):
                d=results[mode].loc['2020':'2025']
                dates=pd.DatetimeIndex([pd.Timestamp('2019-12-31')]).append(d.index)
                wealth=np.r_[10.,10*(1+d['return']).cumprod()]
                dd=wealth/np.maximum.accumulate(wealth)-1
                axes[0].plot(dates,wealth,color=color,label=name,lw=1.4)
                axes[1].plot(dates,dd*100,color=color,lw=1.2)
            axes[0].set_ylabel('Account value (USD 10,000)')
            axes[0].legend(fontsize=9,ncol=3,loc='upper left')
            axes[1].set_ylabel('Drawdown (%)');axes[1].set_xlabel('Year')
            for ax in axes:ax.grid(alpha=.15)
            fig.tight_layout();fig.savefig(out/'plain_journey.png',dpi=150);plt.close(fig)
    (out/'BEGINNER.md').write_text('''# Figures

![Fixed-rule performance](plain_comparison.png)

**Figure 1.** Fixed-rule performance in 2007–2025 and 2020–2025. Each column shares a common scale across periods. Return and volatility are annualized; maximum drawdown is shown as a positive loss magnitude. All results include assumed transaction costs.

![Account values and drawdowns](plain_journey.png)

**Figure 2.** Strategy accounts rebased to USD 100,000 at year-end 2019, retaining their existing holdings. The upper panel shows account values on a linear scale. The lower panel measures losses relative to each account's running peak within the displayed period. Rebasement does not represent a new investment or include currency conversion.

Volatility measures the dispersion of daily returns; drawdown measures a realized peak-to-trough loss. A lower volatility estimate does not imply a smaller maximum loss.

[Research report](REPORT.md) · [Numerical comparison](COMPARISON.md)
''',encoding='utf-8')

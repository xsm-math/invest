"""Auditable data retrieval and strict local CSV validation."""
from pathlib import Path
import hashlib, json, urllib.request
import numpy as np
import pandas as pd

def download(path, start='2005-01-01', end='2026-01-01'):
    """Yahoo public chart endpoint: end exclusive; save raw response for audit."""
    p1 = int(pd.Timestamp(start, tz='UTC').timestamp())
    p2 = int(pd.Timestamp(end, tz='UTC').timestamp())
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/GLD?period1={p1}&period2={p2}&interval=1d'
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.with_suffix('.raw.json').write_bytes(raw)
    return convert(raw, path, url)

def convert(raw, path, url='Yahoo Finance chart API; initial retrieval'):
    j = json.loads(raw)['chart']['result'][0]
    q = j['indicators']['quote'][0]
    dates = pd.to_datetime(j['timestamp'], unit='s', utc=True).tz_convert('America/New_York').tz_localize(None).normalize()
    out = pd.DataFrame({'Date':dates, 'AdjClose':j['indicators']['adjclose'][0]['adjclose'], 'Close':q['close']})
    out.to_csv(path, index=False)
    meta = {'symbol':'GLD','currency':'USD','source':url,'retrieved_utc':pd.Timestamp.now(tz='UTC').isoformat(),
            'rows':len(out),'first':str(dates.min().date()),'last':str(dates.max().date()),
            'csv_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'adjustment':'Yahoo AdjClose; raw Close also retained; no additional management fee deducted'}
    path.with_suffix('.metadata.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')
    return out

def load_prices(path):
    d = pd.read_csv(path)
    if not {'Date','AdjClose'}.issubset(d.columns):
        raise ValueError('CSV requires Date,AdjClose columns')
    d['Date'] = pd.to_datetime(d['Date'], errors='raise')
    if d.Date.duplicated().any() or not d.Date.is_monotonic_increasing:
        raise ValueError('Dates must be unique and increasing; fix source, do not silently sort')
    p = pd.Series(pd.to_numeric(d.AdjClose, errors='raise').to_numpy(), index=pd.DatetimeIndex(d.Date), name='price')
    if not np.isfinite(p).all() or (p <= 0).any():
        raise ValueError('Prices must be finite, positive, without missing values')
    if p.index.to_series().diff().dt.days.max() > 7:
        raise ValueError('Data gap >7 calendar days; investigate missing sessions')
    if p.pct_change(fill_method=None).abs().max() > .30:
        raise ValueError('Daily move >30%; investigate adjustment/data errors')
    return p

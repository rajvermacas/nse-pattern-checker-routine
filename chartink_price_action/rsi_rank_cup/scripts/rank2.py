import pandas as pd, numpy as np, json, datetime as dt

IST = 5.5*3600
def day(ts): return dt.datetime.utcfromtimestamp(int(ts)+IST).strftime('%Y-%m-%d')

dd = pd.read_parquet('cup/daily.parquet').sort_values(['symbol','ts'])
hh = pd.read_parquet('cup/hourly_closed.parquet').sort_values(['symbol','ts'])
dd['d'] = dd['ts'].map(day); hh['d'] = hh['ts'].map(day)

hd = hh.groupby(['symbol','d']).agg(open=('open','first'), high=('high','max'),
     low=('low','min'), close=('close','last'), volume=('volume','sum')).reset_index()

TARGET = max(dd['d'].max(), hd['d'].max())
print('target as-of date:', TARGET)

def wilder_rsi(c, n=14):
    c = np.asarray(c, float); d = np.diff(c)
    up = np.where(d>0,d,0.); dn = np.where(d<0,-d,0.)
    au, ad = up[:n].mean(), dn[:n].mean()
    for i in range(n, len(d)):
        au = (au*(n-1)+up[i])/n; ad = (ad*(n-1)+dn[i])/n
    return 100.0 if ad==0 else 100-100/(1+au/ad)

rows=[]; patched=[]; rescaled=[]
for sym, g in dd.groupby('symbol'):
    g = g.copy()
    have = set(g['d'])
    hg = hd[hd.symbol==sym]
    miss = [d for d in hg['d'] if d not in have and d > g['d'].max()]
    if miss:
        # scale guard: compare last common day's close (TDPOWERSYS daily is split-corrupted)
        common = hg[hg['d'].isin(have)]
        ratio = 1.0
        if len(common):
            ld = common['d'].max()
            dc = float(g.loc[g.d==ld,'close'].iloc[-1]); hc = float(common.loc[common.d==ld,'close'].iloc[-1])
            if dc>0 and abs(hc/dc-1) > 0.02:
                ratio = dc/hc; rescaled.append((sym, round(hc/dc,3)))
        add = hg[hg['d'].isin(miss)].copy()
        for c in ['open','high','low','close']: add[c] *= ratio
        g = pd.concat([g[['d','close']], add[['d','close']]]).sort_values('d')
        patched.append(sym)
    else:
        g = g[['d','close']]
    rows.append({'symbol':sym, 'bars':len(g), 'rsi14':round(wilder_rsi(g['close'].values),2),
                 'close':round(float(g['close'].values[-1]),2), 'asof':g['d'].max(),
                 'patched': sym in patched})

r = pd.DataFrame(rows).sort_values('rsi14',ascending=False).reset_index(drop=True); r.index+=1
json.dump(r.to_dict('records'), open('rsi15/ranking.json','w'), indent=1)
pd.set_option('display.width',200)
print(r.head(20).to_string())
print('\npatched %d symbols; rescaled: %s' % (len(patched), rescaled))
print('asof spread:', r.asof.value_counts().to_dict())
print('\nTOP15:', ','.join(r.head(15).symbol))

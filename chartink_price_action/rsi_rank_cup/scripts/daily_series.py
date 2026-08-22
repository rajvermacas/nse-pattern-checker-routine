import pandas as pd, numpy as np, datetime as dt
IST = 5.5*3600
def day(ts): return dt.datetime.utcfromtimestamp(int(ts)+IST).strftime('%Y-%m-%d')

def load_all(root='.'):
    dd = pd.read_parquet(f'{root}/cup/daily.parquet').sort_values(['symbol','ts'])
    hh = pd.read_parquet(f'{root}/cup/hourly_closed.parquet').sort_values(['symbol','ts'])
    dd['d']=dd['ts'].map(day); hh['d']=hh['ts'].map(day)
    hd = hh.groupby(['symbol','d']).agg(open=('open','first'),high=('high','max'),
         low=('low','min'),close=('close','last'),volume=('volume','sum')).reset_index()
    out={}
    for sym,g in dd.groupby('symbol'):
        g=g[['d','open','high','low','close','volume']].copy()
        hg=hd[hd.symbol==sym]; have=set(g['d'])
        miss=[x for x in hg['d'] if x not in have and x>g['d'].max()]
        if miss:
            common=hg[hg['d'].isin(have)]; ratio=1.0
            if len(common):
                ld=common['d'].max()
                dc=float(g.loc[g.d==ld,'close'].iloc[-1]); hc=float(common.loc[common.d==ld,'close'].iloc[-1])
                if dc>0 and abs(hc/dc-1)>0.02: ratio=dc/hc
            add=hg[hg['d'].isin(miss)][['d','open','high','low','close','volume']].copy()
            for c in ['open','high','low','close']: add[c]*=ratio
            g=pd.concat([g,add],ignore_index=True)
        out[sym]=g.sort_values('d').reset_index(drop=True)
    return out

def ema(x,n):
    x=np.asarray(x,float); a=2/(n+1); o=np.empty_like(x); o[0]=x[0]
    for i in range(1,len(x)): o[i]=a*x[i]+(1-a)*o[i-1]
    return o

def rsi_series(c,n=14):
    c=np.asarray(c,float); d=np.diff(c)
    up=np.where(d>0,d,0.); dn=np.where(d<0,-d,0.)
    out=np.full(len(c),np.nan); au=up[:n].mean(); ad=dn[:n].mean()
    out[n]=100.0 if ad==0 else 100-100/(1+au/ad)
    for i in range(n,len(d)):
        au=(au*(n-1)+up[i])/n; ad=(ad*(n-1)+dn[i])/n
        out[i+1]=100.0 if ad==0 else 100-100/(1+au/ad)
    return out

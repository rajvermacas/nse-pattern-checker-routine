import json, os, math, datetime
import numpy as np

BASE=os.path.dirname(os.path.abspath(__file__))
D=os.path.join(BASE,'data')
IST=datetime.timezone(datetime.timedelta(hours=5,minutes=30))

def ema(a,n):
    a=np.asarray(a,float); k=2/(n+1); out=np.empty_like(a); out[0]=a[0]
    for i in range(1,len(a)): out[i]=a[i]*k+out[i-1]*(1-k)
    return out
def rsi(c,n=14):
    c=np.asarray(c,float); d=np.diff(c); g=np.where(d>0,d,0); l=np.where(d<0,-d,0)
    ag=g[:n].mean(); al=l[:n].mean(); out=[np.nan]*(n)
    for i in range(n,len(d)+1):
        if i>n:
            ag=(ag*(n-1)+g[i-1])/n; al=(al*(n-1)+l[i-1])/n
        out.append(100 if al==0 else 100-100/(1+ag/al))
    return np.array(out[:len(c)],float)
def atr(h,l,c,n=14):
    h,l,c=map(lambda x: np.asarray(x,float),(h,l,c))
    tr=np.maximum(h[1:]-l[1:],np.maximum(abs(h[1:]-c[:-1]),abs(l[1:]-c[:-1])))
    tr=np.concatenate([[h[0]-l[0]],tr]); out=np.empty(len(tr)); out[0]=tr[:n].mean()
    for i in range(1,len(tr)): out[i]=(out[i-1]*(n-1)+tr[i])/n
    return out
def adx(h,l,c,n=14):
    h,l,c=map(lambda x: np.asarray(x,float),(h,l,c))
    up=h[1:]-h[:-1]; dn=l[:-1]-l[1:]
    pdm=np.where((up>dn)&(up>0),up,0.); ndm=np.where((dn>up)&(dn>0),dn,0.)
    tr=np.maximum(h[1:]-l[1:],np.maximum(abs(h[1:]-c[:-1]),abs(l[1:]-c[:-1])))
    def sm(x):
        o=np.empty(len(x)); o[0]=x[:n].sum()
        for i in range(1,len(x)): o[i]=o[i-1]-o[i-1]/n+x[i]
        return o
    st,sp,sn=sm(tr),sm(pdm),sm(ndm)
    pdi=100*sp/np.where(st==0,1e-9,st); ndi=100*sn/np.where(st==0,1e-9,st)
    dx=100*abs(pdi-ndi)/np.where((pdi+ndi)==0,1e-9,pdi+ndi)
    a=np.empty(len(dx)); a[:n]=np.nan; a[n]=dx[1:n+1].mean() if len(dx)>n else np.nan
    for i in range(n+1,len(dx)): a[i]=(a[i-1]*(n-1)+dx[i])/n
    return a[-1],pdi[-1],ndi[-1]
def pivots(h,l,k=3):
    ph=[];pl=[]
    for i in range(k,len(h)-k):
        if h[i]==max(h[i-k:i+k+1]): ph.append((i,h[i]))
        if l[i]==min(l[i-k:i+k+1]): pl.append((i,l[i]))
    return ph,pl
def pct(a,b): return round((a/b-1)*100,2) if b else None

def analyze(sym):
    r=json.load(open(os.path.join(D,f'{sym}.json')))
    H=r.get('hourly'); DD=r.get('daily')
    if not H or len(H)<120: return None
    # backfill missing final daily bar(s) from hourly (Yahoo daily range often lags a session)
    if DD:
        import collections
        lastd=datetime.datetime.fromtimestamp(DD[-1][0],IST).date()
        byday=collections.OrderedDict()
        for b in H:
            d=datetime.datetime.fromtimestamp(b[0],IST).date()
            byday.setdefault(d,[]).append(b)
        for d,bs in byday.items():
            if d>lastd:
                DD.append([bs[0][0],bs[0][1],max(x[2] for x in bs),min(x[3] for x in bs),bs[-1][4],sum(x[5] for x in bs)])
    ts=[x[0] for x in H]; o=[x[1] for x in H]; h=[x[2] for x in H]; l=[x[3] for x in H]; c=[x[4] for x in H]; v=[x[5] for x in H]
    c_=np.array(c,float); h_=np.array(h,float); l_=np.array(l,float); v_=np.array(v,float)
    e20,e50,e200=ema(c_,20),ema(c_,50),ema(c_,200) if len(c_)>=200 else (ema(c_,20),ema(c_,50),ema(c_,min(200,len(c_))))
    e20,e50=ema(c_,20),ema(c_,50); e200=ema(c_,200)
    R=rsi(c_,14); A=atr(h_,l_,c_,14); adxv,pdi,ndi=adx(h_,l_,c_,14)
    last=c_[-1]
    ph,pl=pivots(h,l,3)
    rec_ph=[p for p in ph if p[0]>=len(h)-160][-6:]
    rec_pl=[p for p in pl if p[0]>=len(l)-160][-6:]
    hi60=float(h_[-60:].max()); lo60=float(l_[-60:].min())
    hi30=float(h_[-30:].max()); lo30=float(l_[-30:].min())
    hiall=float(h_.max()); loall=float(l_.min())
    idx_hi=int(np.argmax(h_[-160:])); bars_since_hi=160-1-idx_hi if len(h_)>=160 else int(len(h_)-1-np.argmax(h_))
    rng30=(hi30-lo30)/last*100
    vol20=float(v_[-20:].mean()); vol100=float(v_[-100:].mean())
    up_v=float(v_[-40:][c_[-40:]>np.array(o[-40:])].sum()); dn_v=float(v_[-40:][c_[-40:]<=np.array(o[-40:])].sum())
    # daily context
    dctx={}
    if DD and len(DD)>60:
        dc=np.array([x[4] for x in DD],float); dh=np.array([x[2] for x in DD],float); dl=np.array([x[3] for x in DD],float)
        d20,d50,d200=ema(dc,20),ema(dc,50),ema(dc,min(200,len(dc)))
        dA=atr(dh,dl,dc,14)
        dctx={'d_close':round(float(dc[-1]),2),'pct_from_52wh':pct(float(dc[-1]),float(dh.max())),
              'pct_from_52wl':pct(float(dc[-1]),float(dl.min())),
              'pct_vs_d20ema':pct(float(dc[-1]),float(d20[-1])),'pct_vs_d50ema':pct(float(dc[-1]),float(d50[-1])),
              'pct_vs_d200ema':pct(float(dc[-1]),float(d200[-1])),
              'd_atr_pct':round(float(dA[-1])/float(dc[-1])*100,2),
              'ret_5d':pct(float(dc[-1]),float(dc[-6])),'ret_20d':pct(float(dc[-1]),float(dc[-21])),
              'ret_60d':pct(float(dc[-1]),float(dc[-61])) if len(dc)>61 else None,
              'd_rsi14':round(float(rsi(dc,14)[-1]),1)}
    recent=[{'t':datetime.datetime.fromtimestamp(ts[i],IST).strftime('%Y-%m-%d %H:%M'),
             'o':o[i],'h':h[i],'l':l[i],'c':c[i],'v':v[i]} for i in range(len(ts)-80,len(ts))]
    return {
      'symbol':sym,'bars_hourly':len(H),
      'last_bar_ist':recent[-1]['t'],'last_close':round(float(last),2),
      'hourly':{
        'ema20':round(float(e20[-1]),2),'ema50':round(float(e50[-1]),2),'ema200':round(float(e200[-1]),2),
        'pct_vs_ema20':pct(last,float(e20[-1])),'pct_vs_ema50':pct(last,float(e50[-1])),'pct_vs_ema200':pct(last,float(e200[-1])),
        'ema_stack_bullish':bool(e20[-1]>e50[-1]>e200[-1]),
        'rsi14':round(float(R[-1]),1),'rsi_5bar_ago':round(float(R[-6]),1),
        'adx14':round(float(adxv),1),'plus_di':round(float(pdi),1),'minus_di':round(float(ndi),1),
        'atr14':round(float(A[-1]),2),'atr_pct':round(float(A[-1])/float(last)*100,2),
        'high_60bar':hi60,'low_60bar':lo60,'high_30bar':hi30,'low_30bar':lo30,
        'pct_from_60bar_high':pct(last,hi60),'pct_from_30bar_high':pct(last,hi30),
        'pct_above_30bar_low':pct(last,lo30),
        'range_30bar_pct':round(rng30,2),
        'high_6mo':hiall,'low_6mo':loall,'pct_from_6mo_high':pct(last,hiall),
        'bars_since_160bar_high':int(bars_since_hi),
        'vol_avg20':int(vol20),'vol_avg100':int(vol100),'vol_ratio_20_100':round(vol20/vol100,2) if vol100 else None,
        'last_bar_vol_vs_avg20':round(float(v_[-1])/vol20,2) if vol20 else None,
        'up_vol_vs_down_vol_40bar':round(up_v/dn_v,2) if dn_v else None,
        'recent_pivot_highs':[[int(i),round(float(x),2)] for i,x in rec_ph],
        'recent_pivot_lows':[[int(i),round(float(x),2)] for i,x in rec_pl],
      },
      'daily':dctx,
      'recent_80_hourly_bars':recent,
    }

syms=[f[:-5] for f in sorted(os.listdir(D)) if f.endswith('.json')]
out={}; skipped=[]
for s in syms:
    try:
        a=analyze(s)
        if a: out[s]=a
        else: skipped.append(s)
    except Exception as e: skipped.append(f'{s}:{repr(e)[:80]}')
json.dump(out,open(os.path.join(BASE,'metrics.json'),'w'),indent=1)
print('analyzed',len(out),'skipped',len(skipped),skipped[:10])

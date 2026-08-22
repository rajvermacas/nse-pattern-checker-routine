import json, os, time, threading
import requests
from concurrent.futures import ThreadPoolExecutor

BASE=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(BASE,'data'); os.makedirs(OUT,exist_ok=True)
SYMS=open(os.path.join(BASE,'symbols.txt')).read().split()
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def new_session():
    s=requests.Session()
    s.headers.update({'User-Agent':UA,'Accept':'*/*','Accept-Language':'en-US,en;q=0.9'})
    try: s.get('https://fc.yahoo.com',timeout=15)
    except Exception: pass
    crumb=None
    for _ in range(3):
        try:
            r=s.get('https://query2.finance.yahoo.com/v1/test/getcrumb',timeout=15)
            if r.status_code==200 and r.text.strip(): crumb=r.text.strip(); break
        except Exception: pass
        time.sleep(2)
    return s,crumb

LOCK=threading.Lock()
SESS=new_session()
def refresh():
    global SESS
    with LOCK:
        SESS=new_session()
    return SESS

def chart(sym,interval,rng,tries=5):
    last=None
    for t in range(tries):
        s,crumb=SESS
        p={'interval':interval,'range':rng,'includePrePost':'false','events':'div,split'}
        if crumb: p['crumb']=crumb
        host='query1' if t%2==0 else 'query2'
        try:
            r=s.get(f'https://{host}.finance.yahoo.com/v8/finance/chart/{sym}.NS',params=p,timeout=30)
            if r.status_code==200:
                j=r.json(); res=j.get('chart',{}).get('result')
                if res: return res[0]
                last=str(j.get('chart',{}).get('error'))[:100]
            else:
                last=f'HTTP {r.status_code}'
                if r.status_code in (401,429): refresh(); time.sleep(4+3*t)
        except Exception as e:
            last=repr(e)[:100]
        time.sleep(1.5+1.5*t)
    return {'__error__':last}

def bars(res):
    if not res or '__error__' in res: return None
    ts=res.get('timestamp') or []
    q=res['indicators']['quote'][0]; out=[]
    for i,t in enumerate(ts):
        o,h,l,c,v=q['open'][i],q['high'][i],q['low'][i],q['close'][i],q['volume'][i]
        if None in (o,h,l,c): continue
        out.append([int(t),round(o,2),round(h,2),round(l,2),round(c,2),int(v or 0)])
    return out

def work(sym):
    f=os.path.join(OUT,f'{sym}.json')
    if os.path.exists(f):
        try:
            r=json.load(open(f))
            if r.get('hourly') and len(r['hourly'])>50: return (sym,len(r['hourly']),len(r.get('daily') or []),'cached')
        except Exception: pass
    h=chart(sym,'1h','6mo'); time.sleep(0.6); d=chart(sym,'1d','1y')
    rec={'symbol':sym,'hourly':bars(h),'daily':bars(d)}
    rec['meta']={k:(h.get('meta',{}) or {}).get(k) for k in ('regularMarketPrice','fiftyTwoWeekHigh','fiftyTwoWeekLow','regularMarketTime','exchangeTimezoneName')} if isinstance(h,dict) else {}
    if isinstance(h,dict) and h.get('__error__'): rec['hourly_error']=h['__error__']
    if isinstance(d,dict) and d.get('__error__'): rec['daily_error']=d['__error__']
    json.dump(rec,open(f,'w'))
    time.sleep(0.8)
    return (sym,len(rec['hourly'] or []),len(rec['daily'] or []),rec.get('hourly_error',''))

with ThreadPoolExecutor(max_workers=3) as ex:
    results=list(ex.map(work,SYMS))
ok=[r for r in results if r[1]>50]; bad=[r for r in results if r[1]<=50]
print(f'OK {len(ok)}  BAD {len(bad)}')
for b in bad: print(' BAD',b)
json.dump({'ok':[r[0] for r in ok],'bad':bad},open(os.path.join(BASE,'fetch_status.json'),'w'),indent=1)

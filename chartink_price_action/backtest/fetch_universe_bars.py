"""Fetch ~3y hourly + 5y daily bars for the eligible NSE universe.

Yahoo notes (both cost real time to find):
  * yfinance is unusable behind the egress proxy - curl_cffi's TLS
    impersonation gets reset. Plain requests works.
  * Every request 429s without an fc.yahoo.com cookie + a crumb.
  * range=730d returns ~1075 days of hourly bars; range=2y returns only 729.
    The longer window is the one you want.
"""
import json, os, time, threading, sys
import numpy as np, requests
from concurrent.futures import ThreadPoolExecutor

B = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(B, 'bars'); os.makedirs(OUT, exist_ok=True)
SYMS = open(os.path.join(B, 'universe.txt')).read().split()
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def new_session():
    s = requests.Session()
    s.headers.update({'User-Agent': UA, 'Accept': '*/*', 'Accept-Language': 'en-US,en;q=0.9'})
    try: s.get('https://fc.yahoo.com', timeout=15)
    except Exception: pass
    crumb = None
    for _ in range(3):
        try:
            r = s.get('https://query2.finance.yahoo.com/v1/test/getcrumb', timeout=15)
            if r.status_code == 200 and r.text.strip(): crumb = r.text.strip(); break
        except Exception: pass
        time.sleep(2)
    return s, crumb

LOCK = threading.Lock(); SESS = new_session()
def refresh():
    global SESS
    with LOCK: SESS = new_session()

def chart(sym, interval, rng, tries=5):
    last = None
    for t in range(tries):
        s, crumb = SESS
        p = {'interval': interval, 'range': rng, 'includePrePost': 'false'}
        if crumb: p['crumb'] = crumb
        host = 'query1' if t % 2 == 0 else 'query2'
        try:
            r = s.get(f'https://{host}.finance.yahoo.com/v8/finance/chart/{sym}.NS', params=p, timeout=40)
            if r.status_code == 200:
                res = r.json().get('chart', {}).get('result')
                if res: return res[0]
                last = 'empty'
            else:
                last = f'HTTP {r.status_code}'
                if r.status_code in (401, 429): refresh(); time.sleep(4 + 3 * t)
        except Exception as e:
            last = repr(e)[:80]
        time.sleep(1.2 + 1.2 * t)
    return {'__error__': last}

def arrays(res):
    if not res or '__error__' in res: return None
    ts = res.get('timestamp') or []
    q = res['indicators']['quote'][0]
    o, h, l, c, v = q['open'], q['high'], q['low'], q['close'], q['volume']
    keep = [i for i in range(len(ts)) if None not in (o[i], h[i], l[i], c[i])]
    if len(keep) < 30: return None
    return dict(
        t=np.array([ts[i] for i in keep], dtype=np.int64),
        o=np.array([o[i] for i in keep], dtype=np.float32),
        h=np.array([h[i] for i in keep], dtype=np.float32),
        l=np.array([l[i] for i in keep], dtype=np.float32),
        c=np.array([c[i] for i in keep], dtype=np.float32),
        v=np.array([v[i] or 0 for i in keep], dtype=np.int64))

def work(sym):
    f = os.path.join(OUT, f'{sym}.npz')
    if os.path.exists(f):
        try:
            z = np.load(f)
            if len(z['hc']) > 300: return (sym, len(z['hc']), len(z['dc']), 'cached')
        except Exception: pass
    H = arrays(chart(sym, '1h', '730d')); time.sleep(0.5)
    D = arrays(chart(sym, '1d', '5y'))
    if H is None or D is None: return (sym, 0, 0, 'no data')
    np.savez_compressed(f,
        ht=H['t'], ho=H['o'], hh=H['h'], hl=H['l'], hc=H['c'], hv=H['v'],
        dt=D['t'], do=D['o'], dh=D['h'], dl=D['l'], dc=D['c'], dv=D['v'])
    time.sleep(0.6)
    return (sym, len(H['c']), len(D['c']), '')

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=3) as ex:
        res = list(ex.map(work, SYMS))
    ok = [r for r in res if r[1] > 300]; bad = [r for r in res if r[1] <= 300]
    print(f'OK {len(ok)}  BAD {len(bad)}')
    for b in bad[:40]: print('  BAD', b)
    json.dump({'ok': [r[0] for r in ok], 'bad': bad}, open(os.path.join(B, 'bars_status.json'), 'w'), indent=1)
